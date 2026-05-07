# `index.py`

## `datasette.views.index.IndexView` · *class*

## Summary:
IndexView is an asynchronous web view class that renders the main index page displaying database information, tables, and views with appropriate visibility controls.

## Description:
This class handles HTTP GET requests to serve the Datasette instance's main index page. It processes user permissions, filters databases and their contents based on visibility rules, calculates table statistics, and prepares data for rendering either as an HTML template or JSON format. The view ensures that users only see databases, tables, and views they have permission to access.

## State:
- name (str): Class attribute set to "index" identifying this view
- ds (Datasette instance): Reference to the main Datasette application instance containing databases, URLs, and permission systems
- self.ds.databases (dict): Dictionary of database objects keyed by name
- self.ds.urls (Urls instance): URL generation utilities for creating database paths
- self.ds.cors (bool): CORS configuration flag for response headers

## Lifecycle:
- Creation: Instantiated automatically by Datasette's routing system when handling index requests
- Usage: Called via HTTP GET requests to the index endpoint (e.g., / or /data.json)
- Destruction: Managed by ASGI framework, no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[IndexView.get] --> B[ensure_permissions]
    B --> C[check_visibility(database)]
    C --> D[table_names]
    D --> E[hidden_table_names]
    E --> F[view_names]
    F --> G[check_visibility(view)]
    G --> H[table_counts]
    H --> I[table_columns]
    I --> J[primary_keys]
    J --> K[fts_table]
    K --> L[get_all_foreign_keys]
    L --> M[Sort tables/views]
    M --> N[Render template or JSON]
```

## Raises:
- PermissionError: Raised by ensure_permissions when user lacks view-instance permission
- Various database-related exceptions from database operations (table_names, table_counts, etc.)

## Example:
```python
# This view handles requests to the main index page
# When accessed as GET /:
#   - Renders index.html template with database information
#   - Filters databases, tables, and views based on user permissions
#   - Calculates table counts and relationship statistics
#
# When accessed as GET /data.json:
#   - Returns JSON representation of database information
#   - Uses CustomJSONEncoder for serialization
#   - Includes CORS headers when enabled
```

### `datasette.views.index.IndexView.get` · *method*

## Summary:
Processes database and table information for display or JSON export, handling permissions, visibility filtering, and sorting.

## Description:
This asynchronous method serves as the main entry point for the Datasette index view. It retrieves database information, filters tables and views based on user permissions, calculates table statistics, and prepares data for either HTML rendering or JSON export. The method implements complex visibility logic, table sorting, and pagination-like truncation of results. When the "format" URL variable is set to a non-empty value, it returns JSON data; otherwise, it renders an HTML template with database information.

## Args:
    request: ASGI request object containing:
        - url_vars: Dictionary with "format" key for output format selection
        - args: Query parameters dictionary, including "_sort" for sorting options
        - actor: User identity for permission checking

## Returns:
    Response: HTTP response object containing either:
        - HTML template rendering with database information when no format specified
        - JSON data with database information when format is specified

## Raises:
    None explicitly documented in method signature

## State Changes:
    Attributes READ: self.ds, self.ds.databases, self.ds.urls, self.ds.metadata(), self.ds.cors, self.ds.permission_allowed, self.ds.check_visibility, self.ds.ensure_permissions
    Attributes WRITTEN: None (method is read-only)

## Constraints:
    Preconditions: 
    - Request must contain valid actor for permission checking
    - Database instance must be available via self.ds
    - User must have "view-instance" permission
    - URL variables must contain format parameter
    Postconditions:
    - All returned data respects user visibility permissions for databases and tables
    - Data is properly truncated to TRUNCATE_AT limit (typically 100 items)
    - JSON output contains properly formatted database information with nested table/view data
    - HTML response includes metadata, version information, and private status

## Side Effects:
    - Calls external database methods (table_names, hidden_table_names, view_names, table_columns, primary_keys, fts_table, get_all_foreign_keys, table_counts)
    - Performs permission checking via self.ds.ensure_permissions
    - Makes database queries for table counts and foreign key information
    - Renders HTML template or returns JSON response
    - May perform cryptographic operations (MD5 hashing) for database color generation
    - Sets CORS headers when enabled

