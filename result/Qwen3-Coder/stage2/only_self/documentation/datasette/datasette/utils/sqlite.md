# `sqlite.py`

## `datasette.utils.sqlite.sqlite_version` · *function*

## Summary:
Returns the cached SQLite library version as a tuple of integers for version comparison.

## Description:
This function provides a cached interface to retrieve the SQLite library version. It leverages a global cache to avoid repeatedly establishing database connections to query the version. The first call to this function initializes the cache by calling `_sqlite_version()`, while subsequent calls return the cached result.

## Args:
    None

## Returns:
    tuple[int, ...]: A tuple of integers representing the SQLite version (e.g., (3, 35, 0) for SQLite 3.35.0). The tuple contains major, minor, and patch version numbers as integers.

## Raises:
    None explicitly raised, but may raise sqlite3 exceptions if SQLite connection fails during the initial version query.

## Constraints:
    Preconditions:
    - SQLite library must be available and properly installed
    - The system must allow creation of in-memory databases
    - The first call may raise exceptions if SQLite connection fails
    
    Postconditions:
    - Function returns a tuple of integers representing the SQLite version
    - The returned tuple can be used for version comparisons using standard tuple comparison operators
    - Once initialized, subsequent calls return the same cached value

## Side Effects:
    - On first call: Creates a temporary in-memory SQLite database connection
    - On first call: Performs a single SQL query execution
    - No persistent state changes or file I/O operations
    - Global variable mutation on first call (setting _cached_sqlite_version)

## Control Flow:
```mermaid
flowchart TD
    A[Call sqlite_version()] --> B{Is _cached_sqlite_version None?}
    B -->|Yes| C[Call _sqlite_version()]
    C --> D[Set _cached_sqlite_version]
    D --> E[Return _cached_sqlite_version]
    B -->|No| F[Return _cached_sqlite_version]
```

## Examples:
```python
# First call - establishes cache
version = sqlite_version()
print(version)  # Output: (3, 35, 0) or similar

# Subsequent calls - use cached value
version2 = sqlite_version()
print(version == version2)  # True

# Version comparison
if sqlite_version() >= (3, 35, 0):
    # Use features available in SQLite 3.35.0+
    pass
```

## `datasette.utils.sqlite._sqlite_version` · *function*

## Summary:
Retrieves the SQLite library version as a tuple of integers for version comparison.

## Description:
This function establishes a temporary in-memory SQLite connection to query the SQLite library version. It's designed to provide a reliable way to determine the SQLite version for compatibility checks and feature detection. The function is extracted from inline code to centralize version retrieval logic and avoid repeated database connections.

## Args:
    None

## Returns:
    tuple[int, ...]: A tuple of integers representing the SQLite version (e.g., (3, 35, 0) for SQLite 3.35.0). The tuple contains major, minor, and patch version numbers as integers.

## Raises:
    None explicitly raised, but may raise sqlite3 exceptions if SQLite connection fails.

## Constraints:
    Preconditions:
    - SQLite library must be available and properly installed
    - The system must allow creation of in-memory databases
    
    Postconditions:
    - Function returns a tuple of integers representing the SQLite version
    - The returned tuple can be used for version comparisons using standard tuple comparison operators

## Side Effects:
    - Creates a temporary in-memory SQLite database connection
    - Performs a single SQL query execution
    - No persistent state changes or file I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[Start _sqlite_version()] --> B[Connect to :memory: database]
    B --> C[Execute "select sqlite_version()"]
    C --> D[Fetch result row]
    D --> E[Extract version string]
    E --> F[Split by "."]
    F --> G[Convert each part to int]
    G --> H[Return tuple of integers]
```

## Examples:
```python
# Basic usage
version = _sqlite_version()
print(version)  # Output: (3, 35, 0) or similar

# Version comparison
if _sqlite_version() >= (3, 35, 0):
    # Use features available in SQLite 3.35.0+
    pass
```

## `datasette.utils.sqlite.supports_table_xinfo` · *function*

## Summary:
Determines whether the current SQLite version supports the TABLE_XINFO feature.

## Description:
Checks if the SQLite library version is 3.26.0 or higher, which is required for the TABLE_XINFO feature. This function is used to conditionally enable or disable functionality that depends on newer SQLite capabilities.

## Args:
    None

## Returns:
    bool: True if the SQLite version is 3.26.0 or higher, False otherwise.

## Raises:
    None

## Constraints:
    Preconditions:
    - SQLite library must be available and properly installed
    - The system must allow creation of in-memory databases (for the first call to sqlite_version)
    
    Postconditions:
    - Function returns a boolean indicating version support
    - The result is cached after the first call to sqlite_version()

## Side Effects:
    - On first call: Creates a temporary in-memory SQLite database connection
    - On first call: Performs a single SQL query execution
    - No persistent state changes or file I/O operations
    - Global variable mutation on first call (setting _cached_sqlite_version in sqlite_version)

## Control Flow:
```mermaid
flowchart TD
    A[Call supports_table_xinfo()] --> B[Call sqlite_version()]
    B --> C{SQLite version >= (3, 26, 0)?}
    C -->|Yes| D[Return True]
    C -->|No| E[Return False]
```

## Examples:
```python
# Check if TABLE_XINFO is supported
if supports_table_xinfo():
    # Use TABLE_XINFO features
    pass
else:
    # Fall back to alternative implementation
    pass

# This check is typically used in conditional code paths
# where newer SQLite features are desired but not required
```

## `datasette.utils.sqlite.supports_generated_columns` · *function*

## Summary:
Determines whether the SQLite version supports generated columns feature.

## Description:
Checks if the current SQLite library version is at least 3.31.0, which is the first version to support generated columns. This function is used to conditionally enable features that rely on generated column functionality in Datasette's SQLite integration.

## Args:
    None

## Returns:
    bool: True if SQLite version is 3.31.0 or higher, False otherwise.

## Raises:
    None

## Constraints:
    Preconditions:
    - SQLite library must be available and properly installed
    - The system must allow creation of in-memory databases (for version checking)
    
    Postconditions:
    - Function returns a boolean indicating version compatibility
    - No side effects beyond potential initialization of version cache

## Side Effects:
    - May initialize the SQLite version cache on first call (via sqlite_version())
    - No persistent state changes or file I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[Call supports_generated_columns()] --> B[Call sqlite_version()]
    B --> C[Compare version tuple >= (3, 31, 0)]
    C --> D{Version >= 3.31.0?}
    D -->|Yes| E[Return True]
    D -->|No| F[Return False]
```

## Examples:
```python
# Check if generated columns are supported
if supports_generated_columns():
    # Enable generated column features
    pass
else:
    # Fall back to alternative implementation
    pass

# Typical usage in conditional logic
if supports_generated_columns():
    # Use generated column specific queries
    query = "CREATE TABLE test (id INTEGER, computed_value AS (id * 2) STORED)"
else:
    # Use traditional table definitions
    query = "CREATE TABLE test (id INTEGER, computed_value INTEGER)"
```

