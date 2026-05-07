# `sqlite.py`

## `datasette.utils.sqlite.sqlite_version` · *function*

## Summary:
Returns the cached version of the SQLite library installed in the system.

## Description:
This function provides a cached lookup of the SQLite version by delegating to the internal `_sqlite_version()` function on first call. It ensures that the expensive operation of querying the SQLite library version is performed only once per session, improving performance for repeated calls. This function is part of the datasette utilities for SQLite version management.

## Args:
    None

## Returns:
    tuple[int, ...]: A tuple of integers representing the SQLite version (e.g., (3, 35, 0) for version 3.35.0). The tuple is cached after the first call.

## Raises:
    None

## Constraints:
    Preconditions:
        - The SQLite library must be available and properly installed.
        - The `sqlite3` module must be importable.
        - The `_sqlite_version()` function must be defined and accessible.
    Postconditions:
        - The returned tuple contains only integer values.
        - The tuple length corresponds to the number of version components (typically 3).
        - The function returns the same cached value on subsequent calls.

## Side Effects:
    - On first invocation, creates a temporary in-memory SQLite database connection and executes a SQL query to retrieve the version string.
    - May modify the global variable `_cached_sqlite_version` on first call.

## Control Flow:
```mermaid
flowchart TD
    A[Start sqlite_version()] --> B{Is _cached_sqlite_version None?}
    B -- Yes --> C[Call _sqlite_version()]
    C --> D[Store result in _cached_sqlite_version]
    D --> E[Return _cached_sqlite_version]
    B -- No --> E
```

## Examples:
    >>> sqlite_version()
    (3, 35, 0)

## `datasette.utils.sqlite._sqlite_version` · *function*

## Summary:
Retrieves and parses the SQLite version from the currently installed SQLite library.

## Description:
This function establishes a temporary in-memory SQLite connection to query the SQLite version string, then converts it into a tuple of integers for easy comparison. It is designed to be a lightweight utility for determining SQLite version compatibility or features.

## Args:
    None

## Returns:
    tuple[int, ...]: A tuple of integers representing the SQLite version (e.g., (3, 35, 0) for version 3.35.0).

## Raises:
    None

## Constraints:
    Preconditions:
        - The SQLite library must be available and properly installed.
        - The `sqlite3` module must be importable.
    Postconditions:
        - The returned tuple contains only integer values.
        - The tuple length corresponds to the number of version components (typically 3).

## Side Effects:
    - Creates a temporary in-memory SQLite database connection.
    - Executes a SQL query against the SQLite library.

## Control Flow:
```mermaid
flowchart TD
    A[Start _sqlite_version()] --> B[Connect to :memory: DB]
    B --> C[Execute 'select sqlite_version()']
    C --> D[Fetch result row]
    D --> E[Extract version string]
    E --> F[Split by '.']
    F --> G[Convert each part to int]
    G --> H[Return tuple of ints]
```

## Examples:
    >>> _sqlite_version()
    (3, 35, 0)

## `datasette.utils.sqlite.supports_table_xinfo` · *function*

## Summary:
Determines whether the installed SQLite version supports the TABLE_XINFO pragma feature.

## Description:
This function checks if the SQLite library version installed in the system is at least 3.26.0, which is the version that introduced support for the TABLE_XINFO pragma. This capability is essential for certain advanced database introspection features in Datasette. The function utilizes the `sqlite_version()` utility function to retrieve the current SQLite version and performs a version comparison against the minimum required version.

## Args:
    None

## Returns:
    bool: True if the SQLite version is 3.26.0 or higher, indicating support for TABLE_XINFO pragma. False otherwise.

## Raises:
    None

## Constraints:
    Preconditions:
        - The SQLite library must be available and properly installed.
        - The `sqlite3` module must be importable.
        - The `sqlite_version()` function must be callable and return a valid version tuple.
    Postconditions:
        - The function returns a boolean value indicating version compatibility.
        - The function is idempotent and returns the same result on repeated calls.

## Side Effects:
    - Calls the `sqlite_version()` utility function, which may perform a one-time initialization of a cached version tuple.

## Control Flow:
```mermaid
flowchart TD
    A[Start supports_table_xinfo()] --> B[Call sqlite_version()]
    B --> C[Compare version tuple with (3, 26, 0)]
    C --> D{Version >= (3, 26, 0)?}
    D -- Yes --> E[Return True]
    D -- No --> F[Return False]
```

## Examples:
    >>> supports_table_xinfo()
    True  # if SQLite version is 3.26.0 or higher
    False # if SQLite version is below 3.26.0

## `datasette.utils.sqlite.supports_generated_columns` · *function*

## Summary:
Determines whether the installed SQLite version supports generated columns feature.

## Description:
Checks if the SQLite library version installed in the system is at least 3.31.0, which is the minimum required version for generated columns support. This function encapsulates the version check logic to centralize the decision-making process for feature availability.

## Args:
    None

## Returns:
    bool: True if the SQLite version is 3.31.0 or higher, indicating generated columns support; False otherwise.

## Raises:
    None

## Constraints:
    Preconditions:
        - The SQLite library must be available and properly installed.
        - The `sqlite_version()` function must be callable and return a valid version tuple.
    Postconditions:
        - The function returns a boolean value indicating feature support status.
        - The function performs no side effects beyond calling `sqlite_version()`.

## Side Effects:
    - Calls `sqlite_version()` which may create a temporary in-memory database connection on first invocation.
    - May modify the global variable `_cached_sqlite_version` on first call to `sqlite_version()`.

## Control Flow:
```mermaid
flowchart TD
    A[Start supports_generated_columns()] --> B[Call sqlite_version()]
    B --> C{Version >= (3, 31, 0)?}
    C -- Yes --> D[Return True]
    C -- No --> D[Return False]
    D --> E[End]
```

## Examples:
    >>> supports_generated_columns()
    True

