# `sqlite.py`

## `datasette.utils.sqlite.sqlite_version` · *function*

## Summary:
Returns the cached SQLite version as a tuple of integers for runtime version checking.

## Description:
Provides a cached interface to retrieve the SQLite version, ensuring that the expensive operation of connecting to an in-memory database and querying the version is performed only once per process execution. This function serves as a singleton accessor for SQLite version information used throughout the Datasette application for compatibility checks.

## Args:
    None

## Returns:
    tuple[int, ...]: A tuple of integers representing the SQLite version (e.g., (3, 35, 0) for SQLite 3.35.0). The tuple contains major, minor, and patch version numbers as integers.

## Raises:
    None explicitly raised, but may raise sqlite3 exceptions if SQLite is not properly installed or accessible during the initial version query.

## Constraints:
    Preconditions:
    - SQLite must be available and properly installed in the environment
    - The sqlite3 module must be importable
    - The first call to this function will initialize the cache by calling `_sqlite_version()`
    
    Postconditions:
    - Returns a tuple of integers representing the SQLite version
    - The returned tuple will have at least one element (major version)
    - Subsequent calls return the cached value without re-executing the version query

## Side Effects:
    - On first invocation, creates a temporary in-memory SQLite database connection
    - On first invocation, performs a single SQL query execution against the in-memory database
    - No persistent state changes or file I/O operations after the first call

## Control Flow:
```mermaid
flowchart TD
    A[Call sqlite_version()] --> B{Is _cached_sqlite_version None?}
    B -- Yes --> C[Call _sqlite_version()]
    C --> D[Store result in _cached_sqlite_version]
    D --> E[Return cached version]
    B -- No --> E[Return cached version]
```

## Examples:
```python
# Basic usage for version checking
version = sqlite_version()
if version >= (3, 35, 0):
    # Use newer SQLite features
    pass
else:
    # Fallback for older versions
    pass

# Multiple calls return the same cached value
v1 = sqlite_version()
v2 = sqlite_version()
assert v1 == v2  # True - same cached value
```

## `datasette.utils.sqlite._sqlite_version` · *function*

## Summary:
Retrieves the SQLite version as a tuple of integers for runtime version checking.

## Description:
Connects to an in-memory SQLite database and queries the SQLite version number, returning it as a tuple of integers for easy comparison. This function is designed to provide runtime version detection for SQLite-specific features or compatibility checks.

## Args:
    None

## Returns:
    tuple[int, ...]: A tuple of integers representing the SQLite version (e.g., (3, 35, 0) for SQLite 3.35.0). The tuple contains major, minor, and patch version numbers as integers.

## Raises:
    None explicitly raised, but may raise sqlite3 exceptions if SQLite is not properly installed or accessible.

## Constraints:
    Preconditions:
    - SQLite must be available and properly installed in the environment
    - The sqlite3 module must be importable
    
    Postconditions:
    - Returns a tuple of integers representing the SQLite version
    - The returned tuple will have at least one element (major version)

## Side Effects:
    - Creates a temporary in-memory SQLite database connection
    - Performs a single SQL query execution against the in-memory database
    - No persistent state changes or file I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[Start _sqlite_version()] --> B[Create in-memory DB connection]
    B --> C[Execute "select sqlite_version()"]
    C --> D[Fetch result row]
    D --> E[Extract version string]
    E --> F[Split by "."]
    F --> G[Convert each part to int]
    G --> H[Return as tuple]
```

## Examples:
```python
# Typical usage for version comparison
version = _sqlite_version()
if version >= (3, 35, 0):
    # Use newer SQLite features
    pass
else:
    # Fallback for older versions
    pass
```

## `datasette.utils.sqlite.supports_table_xinfo` · *function*

## Summary:
Determines whether the current SQLite version supports the table XINFO feature.

## Description:
Checks if the SQLite database version is 3.26.0 or higher, which is required for the table XINFO functionality. This function provides a centralized way to perform version compatibility checks throughout the Datasette application.

## Args:
    None

## Returns:
    bool: True if the SQLite version is 3.26.0 or greater, False otherwise.

## Raises:
    None

## Constraints:
    Preconditions:
    - SQLite must be available and properly installed in the environment
    - The sqlite3 module must be importable
    
    Postconditions:
    - Returns a boolean value indicating version compatibility
    - The function is idempotent and returns the same result on subsequent calls

## Side Effects:
    - Calls sqlite_version() which may perform an initial expensive operation to cache the SQLite version
    - No persistent state changes or file I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[Call supports_table_xinfo()] --> B[Call sqlite_version()]
    B --> C{SQLite version >= (3, 26, 0)?}
    C -- Yes --> D[Return True]
    C -- No --> D[Return False]
```

## Examples:
```python
# Check if table XINFO is supported
if supports_table_xinfo():
    # Use table XINFO features
    pass
else:
    # Fall back to alternative implementation
    pass
```

## `datasette.utils.sqlite.supports_generated_columns` · *function*

## Summary:
Determines whether the SQLite version supports generated columns feature.

## Description:
Checks if the current SQLite version is at least 3.31.0, which is the minimum version that introduced support for generated columns. This function enables conditional logic in Datasette to use generated column features when available, while providing fallback behavior for older SQLite installations.

## Args:
    None

## Returns:
    bool: True if the SQLite version is 3.31.0 or higher, indicating support for generated columns; False otherwise.

## Raises:
    None

## Constraints:
    Preconditions:
    - SQLite must be available and properly installed in the environment
    - The sqlite3 module must be importable
    
    Postconditions:
    - Returns a boolean value indicating version compatibility
    - Does not modify any external state

## Side Effects:
    - Calls sqlite_version() which may perform a one-time initialization of cached SQLite version information
    - No persistent state changes or file I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[Call supports_generated_columns()] --> B[Get SQLite version via sqlite_version()]
    B --> C[Compare version tuple with (3, 31, 0)]
    C --> D{Version >= (3, 31, 0)?}
    D -- Yes --> E[Return True]
    D -- No --> F[Return False]
```

## Examples:
```python
# Check if generated columns are supported
if supports_generated_columns():
    # Enable generated column features
    create_table_sql = '''
        CREATE TABLE example (
            id INTEGER PRIMARY KEY,
            name TEXT,
            name_upper AS (UPPER(name)) STORED
        )
    '''
else:
    # Provide alternative implementation for older SQLite versions
    create_table_sql = '''
        CREATE TABLE example (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    '''
```

