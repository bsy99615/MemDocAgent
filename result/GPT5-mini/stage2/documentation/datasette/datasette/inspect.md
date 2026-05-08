# `inspect.py`

## `datasette.inspect.inspect_hash` · *function*

## Summary:
Compute and return the SHA-256 hex digest of the byte contents of a file-like path by reading it in fixed-size blocks to avoid loading the entire file into memory.

## Description:
This function iteratively reads the binary contents of the provided path in blocks, feeds each block into a SHA-256 hasher, and returns the final lowercase hexadecimal digest string.

Known callers within the provided repository snapshot:
    - No direct callers were present in the provided code snapshot. Typical usage is from higher-level inspection or file-processing utilities that need a stable content fingerprint for a file (for cache keys, change detection, or metadata).

Why this is a separate function:
    - Encapsulates the memory-efficient, block-wise hashing pattern (open, read-by-block, update hasher) so callers need not duplicate this boilerplate.
    - Centralizes behavior (e.g., block-size tuning) and ensures consistent digest format (lowercase hex) across the codebase.

## Args:
    path (pathlib.Path or object with .open(mode) -> file-like): A path-like object whose .open("rb") returns a readable binary file object. The function calls path.open("rb") directly; strings or plain os.PathLike objects without .open are not acceptable unless wrapped (e.g., pathlib.Path("...")).

Notes about HASH_BLOCK_SIZE:
    - The function reads using a module-level constant HASH_BLOCK_SIZE. This constant must exist in the same module and be an integer. Typical values are powers of two (e.g., 65536) but any integer is accepted by the underlying file.read call.
    - If HASH_BLOCK_SIZE is undefined, a NameError will be raised at call time.

## Returns:
    str: A 64-character lowercase hexadecimal string representing the SHA-256 digest of the file's bytes.
    - For an empty file, the returned value is the SHA-256 digest of zero bytes (the canonical value for SHA-256(b'')).
    - The return is deterministic for the same byte contents and independent of platform newline handling because the file is read in binary mode.

## Raises:
    NameError: If HASH_BLOCK_SIZE is not defined in the module where this function is declared.
    AttributeError: If the provided path object does not have an .open attribute (e.g., passing a plain str).
    FileNotFoundError / PermissionError / OSError: Any I/O error raised by path.open("rb") or reading from the resulting file object will propagate.
    TypeError: If the object returned by path.open("rb") does not support .read(bytes) semantics expected of a binary file-like object.

## Constraints:
Preconditions:
    - The caller must provide a path-like object with an .open("rb") method (commonly a pathlib.Path instance).
    - The module-level HASH_BLOCK_SIZE must be defined as an integer before calling inspect_hash.
Postconditions:
    - No mutation occurs to the file or external state; the function returns the SHA-256 digest as a hex string.
    - The file is closed before the function returns (using a with-context).

## Side Effects:
    - No external I/O besides reading the specified file.
    - No network calls, database writes, stdout/stderr writes, or modification of global state.
    - The only observable effect is that the file is opened and read (read pointer advances); the file is closed at exit.

## Control Flow:
flowchart TD
    Start --> OpenFile
    OpenFile --> ReadBlock
    ReadBlock --> IsDataEmpty{data == b''?}
    IsDataEmpty -- Yes --> ReturnDigest
    IsDataEmpty -- No --> UpdateHash
    UpdateHash --> ReadBlock
    ReturnDigest --> End

## Examples:
Example using pathlib.Path and handling IO errors:

    from pathlib import Path
    from datasette.inspect import inspect_hash

    p = Path("/path/to/large-file.db")
    try:
        digest = inspect_hash(p)
    except FileNotFoundError:
        # file does not exist
        handle_missing_file()
    except PermissionError:
        # insufficient permissions
        handle_permissions_issue()
    else:
        print("SHA-256 digest:", digest)

Example showing how to call with an object that implements .open("rb") (custom wrapper):

    class Wrapper:
        def __init__(self, filename):
            self._p = Path(filename)
        def open(self, mode="rb"):
            return self._p.open(mode)

    wrapper = Wrapper("/path/to/file")
    digest = inspect_hash(wrapper)
    assert isinstance(digest, str) and len(digest) == 64

## `datasette.inspect.inspect_views` · *function*

## Summary:
Returns a list of all view names defined in the connected SQLite database.

## Description:
This function performs a simple schema query against the provided SQLite connection to enumerate database views. It runs a read-only query against the sqlite_master table and collects the first column of each returned row (the view name).

Known callers within the provided code snapshot:
- No direct callers were found in the provided component snapshot. In typical applications, this function is invoked by higher-level schema inspection or metadata-collection code that needs to list database views for UI presentation, documentation generation, migrations, or integrity checks.

Responsibility boundary:
- This function is a focused helper whose sole responsibility is enumerating view names. It deliberately does not perform any filtering, ordering, or normalization of names, nor does it modify the database. It is extracted into a separate function to centralize the "list views" query and to make tests and callers simpler and clearer.

## Args:
    conn (sqlite3.Connection-like): A connection or connection-like object for an SQLite database.
        - Required methods/behavior: must expose an execute(sql) method that returns an iterable of row-like sequences (rows where the view name is accessible as index 0).
        - Typical type: sqlite3.Connection or object that behaves like a DB-API connection/cursor with execute returning rows of tuples.
        - Interdependencies: The connection must be connected to the database whose views are to be listed.

## Returns:
    list[str]: A list of view names (strings). Each entry corresponds to the "name" column from sqlite_master for rows where type = "view".
    - If there are no views, an empty list is returned.
    - The returned order matches the iteration order from conn.execute; no additional sorting is applied by this function.

## Raises:
    Any exception raised by the underlying connection.execute call may propagate:
    - sqlite3.DatabaseError or subclasses (such as sqlite3.OperationalError) if the SQL fails or the connection is closed.
    - AttributeError if the provided conn does not have an execute method.
    - IndexError can occur if execute yields rows that do not contain a zeroth element (this is unlikely for a standard SQLite response).
    - Other DB-API exceptions as raised by the connection implementation.

## Constraints:
Preconditions:
    - conn must be an active connection to an SQLite database or an object that implements execute(sql) returning row sequences.
    - The connection must support reading sqlite_master (i.e., be connected to a standard SQLite database).

Postconditions:
    - On successful return, the result is a Python list of zero or more strings; the database is unchanged.
    - No transaction state is modified by this function (it only performs a read query).

## Side Effects:
    - Performs a read-only query against the database (no writes, no file/network I/O beyond the DB connection itself).
    - Does not mutate global variables or external caches.
    - No external service calls.

## Control Flow:
flowchart TD
    Start["Start: inspect_views(conn)"]
    CheckConn["Call conn.execute('select name from sqlite_master where type = \"view\"')"]
    Iterate["Iterate over each row v returned"]
    Extract["Extract v[0] (view name) and append to list"]
    Return["Return list of names"]
    Error["Underlying DB/API raises exception -> propagate to caller"]

    Start --> CheckConn
    CheckConn -->|success| Iterate
    CheckConn -->|exception| Error
    Iterate --> Extract
    Extract --> Iterate
    Iterate --> Return

## Examples:
- Typical usage (described):
    Given an open SQLite connection object named conn, call this function to obtain all view names in that database. For example, a caller that builds a schema overview would call this helper, then iterate the returned names to collect column metadata for each view.

- Error handling (described):
    If the connection might be closed or the database file missing, wrap the call in try/except and handle sqlite3.DatabaseError (or the broader exception types your codebase prefers). On exception, decide whether to retry, return an empty list, or surface the error to the user.

- Edge-case behavior:
    If the database contains no views, an empty list is returned. If conn is not an SQLite connection (but provides execute in another way), behavior depends on that object's execute implementation; if it returns rows with the first column being the name, those values will be returned.

## `datasette.inspect.inspect_tables` · *function*

## Summary:
Inspect the SQLite connection and return a metadata mapping for every table found in the database, including columns, primary keys, row count, FTS status, hidden flag, and any discovered foreign-key metadata.

## Description:
This function scans an open SQLite connection to assemble per-table metadata suitable for higher-level database introspection and UI use.

Known callers:
- No direct callers were discovered in the immediate scan of this function alone. Typical callers are database-inspection or metadata-assembly code paths that need a complete view of tables (for example: code that constructs a server's /db/<database> metadata response before rendering or returning JSON).

Why this logic is extracted:
- Inspecting tables requires running several queries and calling helper utilities (column listing, detecting primary keys, foreign keys, FTS, and spatialite detection). Extracting this into a single function centralizes the logic for assembling table metadata, isolates SQL and helper-calls from higher-level code, and makes it easier to test and reuse.

## Args:
    conn (sqlite3.Connection-like):
        - A live SQLite connection object with an execute(sql) method that returns rows accessible by column name (e.g., sqlite3.Row) and supports fetchone().
        - Must be open and usable for reads. The function issues SELECT queries only.
    database_metadata (dict):
        - A mapping containing optional pre-existing metadata for the database.
        - Expected to optionally contain a "tables" key mapping table-name -> per-table metadata (e.g., {"tables": {"mytable": {"hidden": True}}}).
        - The function reads database_metadata.get("tables", {}) but does not modify database_metadata.

## Returns:
    dict[str, dict]: A mapping keyed by table name. Each value is a dictionary with the following keys:
        - name (str): The table name (same as the mapping key).
        - columns (list[str]): Column names for the table as returned by table_columns(conn, table).
        - primary_keys (list[str]): Primary key column names as returned by detect_primary_keys(conn, table).
        - count (int): Number of rows in the table. If counting fails due to sqlite3.OperationalError (e.g., permission or virtual table limitations), this is set to 0.
        - hidden (bool): Whether the table is considered hidden. Defaults to False unless set in database_metadata for that table or matched against the hidden-tables discovery logic.
        - fts_table: Value returned by detect_fts(conn, table). The function stores whatever detect_fts returns (commonly a boolean or FTS index name depending on helper implementation).
        - foreign_keys (optional): Present when get_all_foreign_keys(conn) returns info for the table. The value is whatever structure get_all_foreign_keys provides for that table (typically a list/dict describing foreign key constraints).
    Edge cases:
        - Tables that cannot be counted due to OperationalError receive count = 0.
        - Tables with names that match or start with discovered hidden-table names will have hidden set to True regardless of database_metadata.

## Raises:
    - The function itself catches sqlite3.OperationalError during the row-count query and substitutes count = 0. It does not explicitly raise other exceptions, but will propagate any exceptions thrown by:
        - conn.execute for queries other than the counted select (for example, if the connection object raises on schema queries),
        - table_columns(conn, table), detect_primary_keys(conn, table), detect_fts(conn, table), get_all_foreign_keys(conn), or detect_spatialite(conn) if those helpers raise.
    - Preconditions on conn (valid, open) are required; otherwise connection-related exceptions will propagate.

## Constraints:
    Preconditions:
        - conn must be a working SQLite connection (read-capable).
        - database_metadata should be a mapping (dict-like) or else database_metadata.get will raise AttributeError.
    Postconditions:
        - Returns a mapping containing an entry for every table name returned by querying sqlite_master for type="table".
        - For each table returned, the metadata dictionary will contain at least the keys: name, columns, primary_keys, count, hidden, and fts_table. foreign_keys is added when available.

## Side Effects:
    - Performs multiple SELECT queries against the provided SQLite connection (reads only).
    - Calls out to helper utilities: table_columns, detect_primary_keys, detect_fts, get_all_foreign_keys, detect_spatialite. Any side effects from those helpers (if present) are not caused by this function itself.
    - Does not perform any writes to the database, filesystem, network, or global variables.

## Control Flow:
flowchart TD
    Start --> QueryTables["Query sqlite_master for type='table' -> table_names"]
    QueryTables --> ForEachTable{For each table in table_names}
    ForEachTable --> GetTableMetadata["table_metadata = database_metadata.get('tables', {}).get(table, {})"]
    GetTableMetadata --> TryCount["try: SELECT count(*) FROM <table>"]
    TryCount -->|Success| SetCount["count = fetched value"]
    TryCount -->|sqlite3.OperationalError| SetCountZero["count = 0"]
    SetCount --> GetColumns["column_names = table_columns(conn, table)"]
    SetCountZero --> GetColumns
    GetColumns --> BuildEntry["tables[table] = {name, columns, primary_keys, count, hidden, fts_table}"]
    BuildEntry --> ForEachTable
    ForEachTable --> AfterTableLoop["after table loop"]
    AfterTableLoop --> ForeignKeysQuery["foreign_keys = get_all_foreign_keys(conn)"]
    ForeignKeysQuery --> ApplyFKs["for each (table,info) in foreign_keys: tables[table]['foreign_keys']=info"]
    ApplyFKs --> HiddenTablesQuery["hidden_tables = <query against conn to find hidden tables>"]
    HiddenTablesQuery --> DetectSpatialite{detect_spatialite(conn)?}
    DetectSpatialite -->|True| AddSpatialiteDefaults["hidden_tables += [known spatialite table names] + <additional query results>"]
    DetectSpatialite -->|False| SkipSpatialite
    AddSpatialiteDefaults --> ApplyHiddenFlags["for t in tables: if t == hidden_table or t.startswith(hidden_table): tables[t]['hidden']=True"]
    SkipSpatialite --> ApplyHiddenFlags
    ApplyHiddenFlags --> Return["return tables"]
    Return --> End

Notes:
- The placeholder steps "<query against conn to find hidden tables>" reflect the function executing additional SELECTs to discover hidden tables; the exact SQL is part of the surrounding codebase (not in this snippet).
- The function marks tables as hidden either when database_metadata indicates it, or when a discovered hidden_table name matches the table (or is a prefix of the table name).

## Examples:
Example: Basic usage (error-handling for helper failures)
    try:
        metadata = inspect_tables(conn, database_metadata)
    except Exception as e:
        # If helper functions or conn fail, handle/log here
        raise

Example: Typical consumption
    # After obtaining `metadata`, a caller might extract public tables:
    public_tables = {
        name: info
        for name, info in metadata.items()
        if not info.get("hidden")
    }
    # And present per-table row counts and columns to users:
    for name, info in public_tables.items():
        print(f"{name}: {info['count']} rows; columns: {', '.join(info['columns'])}")

