# `datasette.views`

## Tree:
```
views/
├── database.py
├── index.py
├── row.py
├── special.py
└── table.py
```

## Role:
Provides web interface views for browsing and interacting with Datasette's database content through HTTP endpoints, including database listings, table data, row details, and special administrative functionality.

## Description:
The views module implements Datasette's web interface by handling HTTP requests and generating appropriate responses for database exploration. It serves as the presentation layer that translates database operations into user-friendly web experiences. This module contains specialized view classes for different aspects of Datasette's functionality, from basic database browsing to advanced query execution and administrative tools.

The module is organized around different types of views:
- Database views for exploring database contents (DatabaseView, DatabaseDownload)
- Table views for browsing tabular data with filtering and sorting (TableView, RowView)
- Special views for administrative and debugging functionality (IndexView, LogoutView, AuthTokenView, etc.)
- Query views for executing SQL commands (QueryView)
- Utility views for configuration and debugging (JsonDataView, PermissionsDebugView, etc.)

Primary consumers include Datasette's ASGI application framework, which routes HTTP requests to appropriate view classes based on URL patterns. The module is tightly integrated with Datasette's core architecture, leveraging permission systems, database connections, and plugin hooks to deliver secure and extensible web interfaces.

## Components:
*   **DatabaseView**: Handles database-level views showing tables, views, and queries with permission checks
*   **DatabaseDownload**: Manages database file downloads with security validation
*   **IndexView**: Renders the main index page listing all accessible databases
*   **RowView**: Displays individual table rows with related data and foreign key information
*   **QueryView**: Executes SQL queries with read/write capabilities and permission management
*   **MagicParameters**: Extends dictionary behavior for plugin-defined dynamic parameter resolution
*   **TableView**: Implements table data views with filtering, sorting, and pagination
*   **AllowDebugView**: Debug interface for testing actor/allow permission matching
*   **AuthTokenView**: Handles root token authentication for initial access
*   **JsonDataView**: Serves JSON data with flexible response formats
*   **LogoutView**: Manages user logout functionality
*   **MessagesDebugView**: Debug interface for adding and managing messages
*   **PatternPortfolioView**: Renders pattern portfolio page with instance view permissions
*   **PermissionsDebugView**: Displays permission check history for debugging access control
*   **Row**: Represents a single database row with convenient access methods
*   **display_columns_and_rows**: Processes database rows into display-ready format
*   **_sql_params_pks**: Generates parameterized SQL queries for primary key lookups

## Public API:
*   **DatabaseView(data)**: Handles database-level views showing tables, views, and queries with permission checks
*   **DatabaseDownload.get**: Downloads database files with security validation
*   **IndexView.get**: Renders the main index page listing all accessible databases
*   **RowView.data**: Displays individual table rows with related data and foreign key information
*   **QueryView.data**: Executes SQL queries with read/write capabilities and permission management
*   **MagicParameters**: Extends dictionary behavior for plugin-defined dynamic parameter resolution
*   **TableView.data**: Implements table data views with filtering, sorting, and pagination
*   **AllowDebugView.get**: Debug interface for testing actor/allow permission matching
*   **AuthTokenView.get**: Handles root token authentication for initial access
*   **JsonDataView.get**: Serves JSON data with flexible response formats
*   **LogoutView.get**: Manages user logout functionality
*   **LogoutView.post**: Processes logout POST requests
*   **MessagesDebugView.get**: Debug interface for adding and managing messages
*   **MessagesDebugView.post**: Processes message addition POST requests
*   **PatternPortfolioView.get**: Renders pattern portfolio page with instance view permissions
*   **PermissionsDebugView.get**: Displays permission check history for debugging access control
*   **Row**: Represents a single database row with convenient access methods
*   **display_columns_and_rows**: Processes database rows into display-ready format
*   **_sql_params_pks**: Generates parameterized SQL queries for primary key lookups

## Dependencies:
*   Internal imports:
    *   `datasette.utils` - For utility functions like `actor_matches_allow`, `QueryInterrupted`
    *   `datasette.database` - For database connection and query execution
    *   `datasette.plugins` - For plugin hook integration
    *   `datasette.urls` - For URL generation utilities
    *   `datasette.version` - For version information
*   External imports:
    *   `asyncio` - For asynchronous programming support
    *   `collections` - For ordered dictionary and defaultdict implementations
    *   `datetime` - For timestamp handling
    *   `html` - For HTML escaping
    *   `json` - For JSON serialization/deserialization
    *   `os` - For file system operations
    *   `re` - For regular expression operations
    *   `sqlite3` - For database connectivity
    *   `urllib.parse` - For URL parsing and encoding
    *   `uuid` - For unique identifier generation

## Constraints:
*   All views must inherit from BaseView or appropriate parent classes to maintain consistency
*   Views must properly implement permission checking using Datasette's permission system
*   Database operations must be properly isolated and secured against SQL injection
*   All asynchronous methods must properly await database operations
*   Views must handle edge cases gracefully, including missing databases, invalid parameters, and permission failures
*   Thread safety: Views are stateless and should be safe for concurrent access
*   Initialization: Views depend on properly initialized Datasette instance with configured databases and plugins

---

## Files

- [`database.py`](views/database.md)
- [`index.py`](views/index.md)
- [`row.py`](views/row.md)
- [`special.py`](views/special.md)
- [`table.py`](views/table.md)

