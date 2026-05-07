# `datasette.views`

## Tree:
```
views/
├── database.py
│   ├── DatabaseDownload
│   ├── DatabaseView
│   ├── MagicParameters
│   └── QueryView
├── index.py
│   └── IndexView
├── row.py
│   └── RowView
├── special.py
│   ├── AllowDebugView
│   ├── AuthTokenView
│   ├── JsonDataView
│   ├── LogoutView
│   ├── MessagesDebugView
│   ├── PatternPortfolioView
│   └── PermissionsDebugView
└── table.py
    ├── Row
    ├── TableView
    ├── _sql_params_pks
    └── display_columns_and_rows
```

## Role:
Handles HTTP request processing and data presentation for Datasette's web interface, implementing various view types for databases, tables, rows, and special administrative functions.

## Description:
The views module is responsible for processing HTTP requests and generating appropriate responses for Datasette's web interface. It implements various view classes and utility functions that handle different aspects of data presentation, including database browsing, table listing, row detail views, and special administrative endpoints. This module serves as the bridge between HTTP requests and the underlying Datasette data model, providing structured data for template rendering and handling user interactions.

The module is organized around different types of views:
- Database views for exploring database contents
- Table views for browsing tabular data
- Row views for displaying individual records
- Special views for administrative functions and debugging
- Index views for the main landing page

## Components:
* **DatabaseView**: Handles database-level HTTP requests, providing structured data for rendering database-specific pages including tables, views, and queries.
* **DatabaseDownload**: Processes HTTP requests to download SQLite database files from a Datasette instance.
* **QueryView**: Manages SQL query execution and rendering for database views, supporting both read-only and write operations.
* **MagicParameters**: A dictionary subclass that provides special handling for "magic" parameters through plugin hooks.
* **IndexView**: Renders the main index page displaying database information, tables, and views with appropriate visibility controls.
* **RowView**: Handles displaying individual record data from a database table in Datasette.
* **AllowDebugView**: Provides a web interface for debugging authorization rules by testing actor/allow permission matching.
* **AuthTokenView**: Handles authentication token validation and session establishment for Datasette admin access.
* **JsonDataView**: Serves JSON-formatted data either as a direct JSON response or rendered in an HTML template.
* **LogoutView**: Manages user logout functionality by processing GET and POST requests to invalidate session cookies.
* **MessagesDebugView**: Implements a special administrative view for debugging message handling in Datasette.
* **PatternPortfolioView**: Handles HTTP GET requests for the pattern portfolio page, requiring instance view permission.
* **PermissionsDebugView**: Displays debug information about permission checks performed by the Datasette instance.
* **TableView**: Retrieves and processes table data for display, handling filtering, sorting, pagination, facets, and column expansion.
* **Row**: Represents a single row of data with named cells, providing access to raw and display values.
* **_sql_params_pks**: Constructs a parameterized SQL SELECT query and associated parameters for retrieving a specific table row by its primary key values.
* **display_columns_and_rows**: Formats database table rows and column metadata for web display, handling various data types including foreign keys, binary data, URLs, and unit conversions.

## Public API:
* **DatabaseView(data)**: Creates a database view handler for database information display
* **DatabaseDownload.get(request)**: Handles HTTP GET requests to download database files
* **QueryView.data(request, sql, ...)**: Processes SQL queries for database views
* **MagicParameters.__init__(data, request, datasette)**: Initializes magic parameter handling
* **IndexView.get(request)**: Processes database and table information for display or JSON export
* **RowView.data(request, default_labels)**: Retrieves and prepares data for a specific row
* **AllowDebugView.get(request)**: Processes actor/allow permission debugging
* **AuthTokenView.get(request)**: Validates a root authentication token and establishes session
* **JsonDataView.__init__(datasette, filename, data_callback, needs_request)**: Initializes JSON data view
* **JsonDataView.get(request)**: Returns JSON-formatted data as HTTP response or HTML template
* **LogoutView.get(request)**: Handles GET requests for logout page
* **LogoutView.post(request)**: Handles user logout by clearing authentication cookies
* **MessagesDebugView.get(request)**: Validates instance viewing permissions and renders messages debug template
* **MessagesDebugView.post(request)**: Adds debug messages to Datasette instance
* **PatternPortfolioView.get(request)**: Handles GET requests for pattern portfolio view
* **PermissionsDebugView.get(request)**: Handles GET requests to display permission checking history
* **TableView.data(request, default_labels, _next, _size)**: Retrieves and processes table data for display
* **TableView.post(request)**: Handles POST requests to execute canned SQL queries
* **Row.__init__(cells)**: Initializes a Row object with cell data
* **Row.__getitem__(key)**: Retrieves raw value of a cell by column name
* **Row.display(key)**: Returns formatted display value for a column
* **_sql_params_pks(db, table, pk_values)**: Constructs SQL query for row retrieval by primary key
* **display_columns_and_rows(datasette, database_name, table_name, description, rows, ...)**: Formats table data for web display

## Dependencies:
* **Internal imports**:
  - `datasette.utils`: For utility functions like tilde decoding, URL generation, and permission checking
  - `datasette.database`: For database connection and query execution
  - `datasette.plugins`: For plugin hook integration and magic parameter handling
  - `datasette.version`: For version information
  - `datasette.urls`: For URL generation utilities
* **External imports**:
  - `asgiref.sync`: For synchronous execution of async functions in certain contexts
  - `collections`: For OrderedDict and Counter data structures
  - `datetime`: For timestamp handling in debug views
  - `json`: For JSON serialization and deserialization
  - `os`: For file system operations in database download
  - `re`: For regular expression operations in URL parsing
  - `sqlite3`: For database operations and error handling
  - `urllib.parse`: For URL encoding/decoding operations
  - `typing`: For type annotations

## Constraints:
* **Thread-safety**: Most views are stateless and designed to be thread-safe, with state managed through request objects and Datasette instance attributes
* **Initialization prerequisites**: Views require a properly initialized Datasette instance with configured databases and plugins
* **Permission requirements**: All views enforce appropriate permission checks before processing requests
* **Data consistency**: Views maintain consistency between database metadata and displayed data through proper transaction handling
* **Resource management**: Views properly manage database connections and ensure cleanup of temporary resources
* **URL parameter validation**: Views validate URL parameters and reject malformed or unsafe inputs
* **Security considerations**: Views implement CSRF protection, SQL injection prevention, and proper authentication checks

---

## Files

- [`database.py`](views/database.md)
- [`index.py`](views/index.md)
- [`row.py`](views/row.md)
- [`special.py`](views/special.md)
- [`table.py`](views/table.md)

