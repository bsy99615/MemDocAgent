# `database.py`

## `datasette.views.database.DatabaseView` · *class*

## Summary:
DatabaseView is a data view class responsible for rendering database-specific information and managing access to database resources including tables, views, and queries.

## Description:
DatabaseView extends the base DataView class to provide functionality for displaying database information in the Datasette web interface. It handles requests for database pages, retrieving and filtering database metadata such as tables, views, and canned queries based on user permissions. The class also manages SQL execution capabilities and provides hooks for plugin extensions.

## State:
- name: str - Class attribute identifying this view as "database"
- self.ds: Datasette instance - Reference to the main Datasette application object
- request: ASGI request object - HTTP request being processed
- database_route: str - Decoded database route from URL variables
- database: str - Name of the database being accessed
- visible: bool - Whether the user has permission to view the database
- private: bool - Whether the database access is private
- metadata: dict - Metadata associated with the database
- table_counts: dict - Counts of rows in each table
- hidden_table_names: set - Set of hidden table names
- all_foreign_keys: dict - Foreign key relationships for all tables
- views: list - List of visible views in the database
- tables: list - List of visible tables with detailed metadata
- canned_queries: list - List of visible canned queries
- attached_databases: list - Names of attached databases

## Lifecycle:
- Creation: Instantiated automatically by Datasette routing system when handling database-related requests
- Usage: Called via the data() method which processes HTTP requests and returns a tuple containing template data, context dictionary, and template names for rendering
- Destruction: Managed by Python garbage collection after request completion

## Method Map:
```mermaid
flowchart TD
    A[DatabaseView.data()] --> B[Decode database route]
    B --> C[Get database reference]
    C --> D[Check visibility permissions]
    D --> E[Get database metadata]
    E --> F{SQL query requested?}
    F -- Yes --> G[Validate SQL and delegate to QueryView]
    F -- No --> H[Collect table/view/query information]
    H --> I[Filter views by visibility]
    I --> J[Filter tables by visibility]
    J --> K[Sort tables]
    K --> L[Collect canned queries]
    L --> M[Build database actions hook]
    M --> N[Get attached databases]
    N --> O[Return template data tuple]
```

## Raises:
- NotFound: When the requested database route does not correspond to an existing database
- Forbidden: When the user lacks permission to view the requested database
- InvalidSql: When SQL query validation fails (only when SQL parameter is present)

## Example:
```python
# Typical usage in Datasette routing
# GET /database.db
# Returns database information including tables, views, and queries
# with appropriate permission checking and filtering
```

### `datasette.views.database.DatabaseView.data` · *method*

## Summary:
Retrieves and structures database metadata, tables, views, and queries for display in the database view template.

## Description:
This method serves as the primary data provider for the database view page, collecting and organizing information about a specific database including its tables, views, and canned queries. It handles permission checking, visibility filtering, and prepares data structures for rendering in the HTML template. When a SQL query is provided via request arguments, it delegates to the QueryView for execution and display instead of building the database overview.

## Args:
    request (Request): ASGI HTTP request object containing URL variables and query parameters
    default_labels (bool): Unused parameter, likely for backward compatibility
    _size (int, optional): Page size parameter for query results, passed to QueryView when applicable

## Returns:
    tuple: A 3-tuple containing:
        1. Dictionary with database metadata including name, path, size, tables, views, queries, and permissions
        2. Dictionary with template context variables including database actions, visibility settings, and configuration flags
        3. Tuple of template names to render

## Raises:
    NotFound: When the requested database route does not exist
    Forbidden: When the user lacks permission to view the database
    InvalidSql: When SQL query parameter is provided but contains invalid SELECT statement patterns

## State Changes:
    Attributes READ:
        - self.ds (Datasette instance)
    Attributes WRITTEN:
        - None directly modified

## Constraints:
    Preconditions:
        - Request must contain a valid database route in url_vars
        - User must have appropriate permissions to view the database
        - If SQL parameter is provided, it must be a valid SELECT statement
    Postconditions:
        - All returned data respects user visibility permissions
        - Database metadata is properly inherited and updated
        - Template-ready data structures are constructed
        - SQL parameter validation occurs when present

## Side Effects:
    - Calls external methods for database access and permission checking
    - Makes async calls to retrieve database metadata and visibility status
    - May delegate to QueryView for SQL query execution
    - Invokes plugin hooks for database actions

## `datasette.views.database.DatabaseDownload` · *class*

## Summary:
DatabaseDownload is a view class that handles HTTP GET requests to download SQLite database files from a Datasette instance.

## Description:
The DatabaseDownload class implements the download functionality for SQLite databases within Datasette. It inherits from DataView and processes HTTP GET requests to serve database files as downloads. The class enforces security policies by checking permissions, validating database properties, and handling conditional requests using ETags for efficient caching.

## State:
- name (str): Class attribute set to "database_download", identifying this view in the routing system
- self.ds: Datasette instance reference, inherited from DataView parent class
- request: ASGI request object containing HTTP request details and URL variables

## Lifecycle:
- Creation: Instantiated automatically by Datasette's routing system when a matching URL pattern is encountered
- Usage: Called via the async get() method when an HTTP GET request is made to a database download endpoint
- Destruction: Automatically cleaned up after the ASGI response is sent; no explicit cleanup required

## Method Map:
```mermaid
flowchart TD
    A[GET request] --> B[DatabaseDownload.get()]
    B --> C[ensure_permissions]
    C --> D[get_database]
    D --> E{Database exists?}
    E -->|No| F[DatasetteError(404)]
    E -->|Yes| G{is_memory?}
    G -->|Yes| H[DatasetteError(404)]
    G -->|No| I{allow_download OR is_mutable?}
    I -->|No| J[Forbidden]
    I -->|Yes| K{db.path?}
    K -->|No| L[DatasetteError(404)]
    K -->|Yes| M[Prepare headers]
    M --> N{Has ETag?}
    N -->|Yes| O[Check if-none-match]
    O --> P{Match?}
    P -->|Yes| Q[Response(304)]
    P -->|No| R[Create AsgiFileDownload]
    R --> S[Return AsgiFileDownload]
```

## Raises:
- DatasetteError: Raised when database doesn't exist, is in-memory, or cannot be downloaded
- Forbidden: Raised when database download is forbidden due to settings or mutability
- KeyError: Raised internally when get_database fails to find the requested database

## Example:
```python
# Typical usage would be triggered by a URL like:
# GET /database.db/download

# The view would:
# 1. Validate permissions for view-database-download, view-database, and view-instance
# 2. Retrieve the database instance
# 3. Check if download is allowed and database is downloadable
# 4. Prepare headers including ETag for caching
# 5. Return AsgiFileDownload for the actual file transfer
```

### `datasette.views.database.DatabaseDownload.get` · *method*

## Summary:
Handles HTTP GET requests for downloading database files by validating permissions, checking database properties, and returning an AsgiFileDownload response.

## Description:
This method implements the download functionality for Datasette databases. It validates that the requesting actor has appropriate permissions to download the specified database, verifies that the database is downloadable (not in-memory and has a file path), and generates an HTTP response that streams the database file to the client. The method also handles ETag-based caching and CORS headers when applicable. The database name in the URL is first processed through tilde decoding to handle special characters.

## Args:
    request: ASGI request object containing URL variables and headers with database name in url_vars["database"]

## Returns:
    AsgiFileDownload: Response object that streams the database file to the client

## Raises:
    DatasetteError: When database is invalid, in-memory, or cannot be downloaded (status codes 404)
    Forbidden: When database download is forbidden due to settings or mutability

## State Changes:
    Attributes READ: self.ds (Datasette instance)
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - Request must contain a valid database name in url_vars["database"]
        - Database must exist and be accessible through self.ds.get_database()
        - Request actor must have permission to view database download, view database, and view instance
        - Database must not be in-memory and must have a valid file path
        - Download must be enabled in settings and database must not be mutable
    Postconditions:
        - Returns AsgiFileDownload response with proper headers
        - If ETag matches, returns 304 Not Modified response
        - File download is properly configured with filename and content type

## Side Effects:
    - Performs permission checks via self.ds.ensure_permissions()
    - Reads database file path from self.ds.get_database()
    - May read configuration settings via self.ds.setting()
    - Initiates file streaming via AsgiFileDownload
    - Sets HTTP headers including ETag and Transfer-Encoding

## `datasette.views.database.QueryView` · *class*

*No documentation generated.*

### `datasette.views.database.QueryView.data` · *method*

## Summary:
Handles database query execution and rendering for Datasette's query view, supporting both read-only and write operations with proper permission checking and template rendering.

## Description:
This asynchronous method processes SQL queries for Datasette's database views, handling both read and write operations with appropriate security checks, parameter processing, and template generation. It serves as the core endpoint for executing custom SQL queries and managing query results in the Datasette web interface.

## Args:
    self: The QueryView instance
    request: ASGI request object containing URL variables, query parameters, and HTTP headers
    sql (str): The SQL query to execute
    editable (bool): Whether the query results should be editable (default: True)
    canned_query (str, optional): Name of a predefined query to reference
    metadata (dict, optional): Metadata associated with the query
    _size (int, optional): Page size limit for query results
    named_parameters (list, optional): Explicit list of named parameters in the SQL
    write (bool): Whether to execute the query as a write operation (default: False)

## Returns:
    tuple: For read operations, returns (response_data, extra_template_func, templates, status_code)
    For write operations with POST requests, returns a Response object
    For write operations with GET requests, returns (response_data, extra_template_func, templates)

## Raises:
    NotFound: When the requested database route doesn't exist
    Forbidden: When user lacks permission to view/query or execute SQL
    sqlite3.DatabaseError: When SQL execution fails

## State Changes:
    Attributes READ: 
        - self.ds (Datasette instance)
        - self.ds.get_database()
        - self.ds.check_visibility()
        - self.ds.ensure_permissions()
        - self.ds.execute()
        - self.ds.permission_allowed()
        - self.ds.databases[database].execute_write()
        - self.ds.add_message()
        - self.ds.urls
        - self.ds.INFO
        - self.ds.ERROR
        - self.ds.settings_dict()
    
    Attributes WRITTEN:
        - self.ds.add_message() (side effect)
        - self.ds.redirect() (side effect)

## Constraints:
    Preconditions:
        - Request must contain valid database route in url_vars
        - SQL query must be valid for the target database
        - User must have appropriate permissions for the requested operation
        - For write operations, database must be mutable
    
    Postconditions:
        - Query results are properly sanitized and formatted for display
        - Appropriate error messages are generated for failed queries
        - Template rendering data is properly structured for view rendering

## Side Effects:
    - Database query execution (read/write)
    - HTTP response generation
    - Session message setting
    - Redirects for write operations
    - Template rendering preparation

## `datasette.views.database.MagicParameters` · *class*

## Summary:
A dictionary subclass that provides magic parameter resolution for Datasette views.

## Description:
MagicParameters extends the standard dictionary to support dynamic parameter resolution through magic prefixes. When accessing a parameter key that starts with an underscore followed by at least two underscores (e.g., "_user_id"), it attempts to resolve the parameter using registered magic functions. This enables features like `_user_id` or `_now` that dynamically compute values based on the request context.

## State:
- `_request`: Request object passed to constructor, used for magic parameter resolution
- `_magics`: Dictionary of magic parameter resolvers obtained from plugin hooks
- All other attributes inherited from the built-in `dict` class

## Lifecycle:
- Creation: Initialize with data dictionary, request object, and datasette instance
- Usage: Access parameters using standard dictionary syntax (`params[key]`)
- Destruction: Inherits standard dict cleanup behavior

## Method Map:
```mermaid
graph TD
    A[MagicParameters.__getitem__] --> B{Key starts with _ and has ≥2 _}
    B -->|Yes| C[Extract prefix from key]
    C --> D[Check if prefix in _magics]
    D -->|Yes| E[Invoke magic resolver with suffix and request]
    E --> F[Return resolved value]
    D -->|No| G[Call super().__getitem__]
    B -->|No| G
```

## Raises:
- KeyError: May be raised by `super().__getitem__()` when key is not found
- Any exceptions raised by registered magic parameter functions

## Example:
```python
# Create instance with initial parameters
params = MagicParameters({'limit': 10}, request, datasette)

# Regular parameter access
limit = params['limit']  # Returns 10

# Magic parameter access (if _user magic is registered)
user_id = params['_user_id']  # Resolves using registered magic function

# If _now magic is registered, gets current timestamp
timestamp = params['_now_timestamp']  # Resolves using registered magic function
```

### `datasette.views.database.MagicParameters.__init__` · *method*

## Summary:
Initializes the MagicParameters object by setting up request context and collecting magic parameters from plugins.

## Description:
This method serves as the constructor for the MagicParameters class. It initializes the parent DataView class with the provided data, stores the HTTP request object for later use, and collects magic parameters from all registered datasette plugins through the plugin system hook mechanism.

## Args:
    data (Any): Data payload passed to the parent DataView constructor
    request (Any): HTTP request object containing request context
    datasette (Datasette): Main Datasette application instance used to query plugin hooks

## Returns:
    None: This method is a constructor and does not return a value

## Raises:
    None explicitly raised: The method delegates to parent constructor and plugin hooks which may raise exceptions, but these are not caught or re-raised by this method

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._request: Stores the provided request object
        - self._magics: Populates with magic parameters from plugin hooks as a dictionary

## Constraints:
    Preconditions:
        - The datasette parameter must be a valid Datasette application instance
        - The request parameter must be a valid HTTP request object
        - The data parameter must be compatible with DataView's constructor requirements
    
    Postconditions:
        - self._request is set to the provided request object
        - self._magics is populated with a dictionary of magic parameters from all plugins
        - The parent DataView is properly initialized with the data parameter

## Side Effects:
    - Calls plugin system hooks (pm.hook.register_magic_parameters)
    - May involve I/O operations during plugin discovery and execution
    - Mutates self._magics attribute with results from plugin hooks

### `datasette.views.database.MagicParameters.__len__` · *method*

## Summary:
Returns the length of the MagicParameters dictionary, ensuring a minimum length of 1.

## Description:
This method overrides the standard `__len__` behavior inherited from `dict` to guarantee that the MagicParameters object always reports a length of at least 1. This prevents issues where an empty parameters dictionary might cause unexpected behavior in downstream code that expects at least one parameter to be present.

The MagicParameters class extends `dict` and supports "magic" parameters that are dynamically resolved through plugin hooks. When the `len()` function is called on a MagicParameters instance, this overridden method ensures that even if no regular parameters exist (empty dict), the object still reports a length of 1.

This override is particularly important for compatibility with code that assumes parameter collections will always have at least one entry, preventing potential bugs in parameter processing pipelines.

## Args:
    None

## Returns:
    int: The length of the underlying dictionary, or 1 if the dictionary is empty.

## Raises:
    None

## State Changes:
    Attributes READ: self (the MagicParameters instance)
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must be properly initialized as a MagicParameters instance.
    Postconditions: The returned value will always be >= 1.

## Side Effects:
    None

### `datasette.views.database.MagicParameters.__getitem__` · *method*

## Summary:
Retrieves values from magic parameters by parsing special keys with underscore prefixes, delegating to registered magic functions or falling back to standard dictionary lookup.

## Description:
This method implements custom parameter resolution logic for keys that start with an underscore and contain at least two underscores. It parses these keys to extract a prefix and suffix, then attempts to resolve them using registered magic parameter handlers. If no handler is found or the handler raises a KeyError, it falls back to standard dictionary access. This enables dynamic parameter resolution for Datasette's view system, allowing plugins to register custom parameter resolvers.

## Args:
    key (str): The parameter key to retrieve, potentially with special underscore formatting

## Returns:
    Any: The resolved value from either a magic parameter handler or standard dictionary lookup

## Raises:
    KeyError: When a magic parameter key cannot be resolved by any registered handler and standard lookup fails

## State Changes:
    Attributes READ: self._magics, self._request
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The instance must have a valid _magics dictionary and _request attribute populated
    Postconditions: Returns either a resolved magic value or performs standard dictionary lookup

## Side Effects:
    None

