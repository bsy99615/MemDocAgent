# `row.py`

## `datasette.views.row.RowView` · *class*

## Summary:
RowView is a data view class responsible for retrieving and rendering individual record (row) data from a database table in Datasette.

## Description:
RowView handles requests for specific records identified by their primary key values within a database table. It implements the data retrieval and presentation logic for displaying individual rows, including fetching the row data, determining visibility permissions, and preparing template data for rendering. The class inherits from DataView and provides specialized functionality for row-level data access.

The class is typically instantiated by the Datasette framework's routing system when handling requests to view specific records, such as `/database/table/pk_values`. It performs authentication checks, executes database queries to fetch the requested row, and prepares structured data for template rendering.

## State:
- name (str): Class attribute set to "row", identifying this view type
- self.ds: Datasette instance reference for accessing databases, metadata, and utilities
- request: ASGI request object containing URL variables and query parameters
- database_route: Decoded database route from URL variables
- table: Decoded table name from URL variables
- pk_values: List of primary key values extracted from URL variables and decoded

## Lifecycle:
- Creation: Instantiated by Datasette's routing mechanism with appropriate dependencies
- Usage: Called via the `data()` method when handling requests for specific record views
- Destruction: Managed by Python's garbage collection after request completion

## Method Map:
```mermaid
flowchart TD
    A[RowView.data()] --> B[Decode URL variables]
    B --> C[Get database reference]
    C --> D[Check visibility permissions]
    D --> E[Validate access]
    E --> F[Extract primary key values]
    F --> G[Execute database query]
    G --> H[Process results]
    H --> I[Prepare template data]
    I --> J[Return data tuple]
    J --> K[RowView.foreign_key_tables()]
    K --> L[Fetch foreign key tables]
```

## Raises:
- NotFound: Raised when database is not found, or when the requested record does not exist
- Forbidden: Raised when the user lacks permission to view the requested table or database

## Example:
```python
# Typical usage in Datasette routing
# Request: GET /mydb/mytable/123
# Result: Fetches row with primary key value 123 from mydb.mytable table
# Returns structured data for template rendering with row details and metadata

# The data() method returns a tuple of:
# 1. Data dictionary containing database info, row data, columns, etc.
# 2. Async template_data function that generates template context
# 3. Tuple of template names to try for rendering
```

### `datasette.views.row.RowView.data` · *method*

## Summary:
Retrieves and formats detailed data for a specific table row, including metadata, display formatting, and template context for rendering.

## Description:
This asynchronous method handles the retrieval and processing of a single database row identified by its primary key values. It performs permission checks, executes a database query to fetch the row data, processes the data for display formatting, and prepares template context data for rendering the row view. The method is designed to be called as part of the HTTP request handling pipeline for row-specific views.

## Args:
    request: ASGI request object containing URL variables and query parameters
    default_labels: Boolean flag (default False) - currently unused in the implementation

## Returns:
    tuple: A 3-tuple containing:
        - data (dict): Core row data including database name, table name, raw rows, columns, primary keys, and units
        - template_data (async callable): Async function returning template context data including display columns, display rows, foreign key tables, and metadata
        - template_names (tuple): Tuple of suggested template names for rendering the row view

## Raises:
    NotFound: When the requested database is not found, or when the record with specified primary keys does not exist
    Forbidden: When the requesting actor lacks permission to view the table

## State Changes:
    Attributes READ: self.ds (Datasette instance), self.ds.metadata, self.ds.table_metadata
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The request must contain valid URL variables for database, table, and pks
        - The database specified in URL variables must exist
        - The user must have appropriate permissions to view the table and database
        - The primary key values must uniquely identify a single row in the table
    Postconditions:
        - If successful, returns a tuple with properly formatted data and template context
        - If no matching row is found, raises NotFound exception

## Side Effects:
    - Database query execution via self.ds.get_database() and db.execute()
    - Permission checking via self.ds.check_visibility()
    - Template context preparation involving async operations
    - Potential I/O operations for database queries and metadata lookups

### `datasette.views.row.RowView.foreign_key_tables` · *method*

## Summary:
Retrieves and constructs metadata about tables that reference the current row via foreign key relationships.

## Description:
This method is responsible for identifying all incoming foreign key relationships to the current table and counting how many records in each referencing table point to the specific row identified by the primary key values. It generates links to those referencing tables and provides count information for navigation purposes.

The method is called during the rendering of a row detail view to display related tables that reference this particular record.

## Args:
    database (str): Name of the database containing the table
    table (str): Name of the table being viewed
    pk_values (list[str]): List of primary key values for the current row (expected to contain exactly one value)

## Returns:
    list[dict]: A list of dictionaries, each representing an incoming foreign key relationship with additional metadata including:
        - count: Number of records in the referencing table that point to this row
        - link: URL to navigate to the referencing table filtered by the current row's primary key
        - other_table: Name of the referencing table
        - other_column: Name of the foreign key column in the referencing table
        - column: Name of the primary key column in the current table
        - table: Name of the current table
        - foreign_key_tables: Empty list if no incoming foreign keys exist

## Raises:
    QueryInterrupted: When a database query is interrupted during execution, resulting in an empty list being returned

## State Changes:
    Attributes READ: self.ds
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The pk_values list must contain exactly one value
        - The database and table must exist and be accessible
        - The current user must have appropriate permissions to view the database and table
    Postconditions:
        - Returns a list of dictionaries describing foreign key relationships
        - Each dictionary contains count, link, and foreign key metadata
        - Returns empty list if no incoming foreign keys exist or if pk_values length is not 1

## Side Effects:
    - Executes database queries to count related records
    - Makes calls to self.ds.urls.table() to construct navigation URLs

