# `sql_functions.py`

## `datasette.sql_functions.prepare_connection` · *function*

## Summary:
Registers the Datasette full-text-search escaping helper as a one-argument SQL scalar function named "escape_fts" on a given SQLite connection so SQL executed on that connection can call it.

## Description:
This function attaches the Python helper (datasette.utils.escape_fts) to a SQLite connection by calling the connection's create_function API with name "escape_fts" and arity 1. After calling this function, SQL executed on that connection can invoke escape_fts(x) to obtain the escaped/quoted form of an FTS query fragment.

Known callers within the codebase:
- No direct callers of prepare_connection were discovered in the available codebase memory snapshot used for this documentation. That does not mean the function is unused at runtime; rather, it is intended to be invoked immediately after opening or obtaining a sqlite3.Connection or a connection-like wrapper.
- Typical call sites (where this should be invoked):
    - Connection setup code that initializes a sqlite3.Connection instance for a database file or in-memory DB.
    - Connection factory or pool initialization routines that prepare each new connection before use.
    - Framework/plugin hooks that run when a new connection is created or handed to application code.

Why this logic is extracted:
- Centralizes the registration of the SQL function name and arity in one place so all connection setup paths register the same handler consistently.
- Keeps connection initialization code concise and avoids duplication of the escape_fts binding.
- Makes it easier to test and mock SQL function registration in unit tests.

## Args:
    conn (sqlite3.Connection or connection-like object): Required.
        - Expected to be an instance of sqlite3.Connection from the standard library, or any object that implements:
            create_function(name: str, num_params: int, func: callable)
        - The function will call conn.create_function("escape_fts", 1, escape_fts).
        - If conn does not provide create_function, an AttributeError will be raised at call time.

## Returns:
    None
    - This function performs an in-place mutation of the connection object by registering a callable under the name "escape_fts". It does not return any value.

## Raises:
    AttributeError:
        - Raised when the provided conn object has no attribute create_function (for example, wrong object type or a closed connection wrapper that does not expose this API).
    sqlite3.Error or other exceptions from the underlying DB API:
        - Any exception raised by conn.create_function (for example, sqlite3.OperationalError, TypeError if the handler is invalid) will propagate through this function unchanged.
    Note: The function itself does not raise exceptions from escape_fts at registration time because the callable is stored as-is; errors from calling escape_fts occur later when SQL invokes it.

## Constraints:
    Preconditions:
        - conn must be an open, usable SQLite connection or wrapper exposing create_function.
        - datasette.utils.escape_fts must be importable and be a callable that accepts one string argument (this is true in the codebase: escape_fts(query) -> str).

    Postconditions:
        - After successful execution, conn has an SQL-callable function named "escape_fts" that accepts exactly one argument and delegates to datasette.utils.escape_fts when invoked from SQL.
        - No filesystem, network, or global state is modified by this call; the change is limited to the in-memory connection state.

## Side Effects:
    - Mutates the in-memory registration of scalar functions on the connection object (no persistent database writes).
    - No file I/O or network I/O is performed by this function itself.
    - No global variables are modified; registration is local to the provided connection.

## Control Flow:
flowchart TD
    Start[Start] --> HasCreate{conn has create_function attribute?}
    HasCreate -- Yes --> Register[Call conn.create_function("escape_fts", 1, escape_fts)]
    Register --> Success[Return None (registration succeeded)]
    HasCreate -- No --> RaiseAttr[AttributeError raised when accessing/create_function]
    RaiseAttr --> End[End]

## Examples (realistic usage described as steps and SQL examples):
Usage scenario — prepare and use a connection with escape_fts:
1. Obtain or open a sqlite3 connection object (for a file-backed DB or an in-memory DB).
2. Immediately call prepare_connection(conn) to register the escape_fts function on that connection.
3. Use the registered function inside SQL statements executed on that connection:
    - Example SQL expression: SELECT escape_fts(:user_input)
    - Example SQL usage in WHERE for FTS: SELECT * FROM documents WHERE documents MATCH escape_fts(:user_input);
4. Error handling:
    - If the object passed as conn is not a connection-like object, catch AttributeError around prepare_connection and log or re-create the connection correctly.
    - If conn.create_function raises sqlite3.Error, handle or propagate that exception according to the application's error policy.

Notes:
- The prepared SQL function allows safe quoting/escaping of terms for SQLite full-text search queries by delegating to datasette.utils.escape_fts; prepare_connection itself does not perform escaping, only registration.
- Because sqlite3's create_function binds a Python callable, the actual escaping will run when SQL invokes escape_fts; registration is cheap and typically performed once per new connection.

