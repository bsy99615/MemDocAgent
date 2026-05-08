# `row.py`

## `datasette.views.row.RowView` · *class*

## Summary:
A view class for displaying individual rows (records) from database tables in Datasette.

## Description:
The RowView class handles the retrieval, formatting, and presentation of individual records from database tables. It processes HTTP requests for specific table rows identified by primary key values and returns structured data suitable for rendering HTML templates. This class is part of Datasette's web interface for viewing individual database records.

## State:
- `name`: Class attribute set to "row" indicating this view's identifier
- Inherits all state from `DataView` parent class including `self.ds` (Datasette instance) and request handling capabilities
- No additional instance attributes beyond those inherited from DataView

## Lifecycle:
- Creation: Instantiated automatically by Datasette's routing system when handling requests to row-specific URLs matching the pattern `/database/table/pk_values`
- Usage: The `data()` method is called by Datasette's ASGI handler to process row view requests
- Destruction: No explicit cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
flowchart TD
    A[Request received] --> B[data()]
    B --> C[Validate database and table access permissions]
    C --> D[Decode URL components (database, table, pks)]
    D --> E[Fetch database and validate existence]
    E --> F[Execute SQL query to retrieve row by primary keys]
    F --> G[Check if row exists]
    G --> H[Format row data for display]
    H --> I[Prepare template data asynchronously]
    I --> J[Return tuple of (data, template_data_func, template_names)]
    
    B --> K[foreign_key_tables()]
    K --> L[Check if single primary key value]
    L --> M[Get incoming foreign key relationships]
    M --> N[Count related records in foreign tables]
    N --> O[Build foreign key table information with counts and links]
    O --> P[Return foreign key table data]
```

## Raises:
- `NotFound`: When database doesn't exist, table doesn't exist, or record with specified primary keys is not found
- `Forbidden`: When user lacks permission to view the requested table or database
- `QueryInterrupted`: When database query execution is interrupted (caught internally in foreign_key_tables)

## Example:
```python
# When accessing a URL like: /mydb/mytable/123

# The data() method returns a tuple with:
# 1. Data dictionary containing row information
data = {
    "database": "mydb",
    "table": "mytable", 
    "rows": [[123, "John", "Doe"]],  # Actual row data
    "columns": ["id", "first_name", "last_name"],  # Column names
    "primary_keys": ["id"],  # Primary key column names
    "primary_key_values": ["123"],  # Values of primary keys from URL
    "units": {}  # Unit metadata for columns
}

# 2. Async template_data function that returns display-ready data
# This function prepares display columns, rows, and metadata for templates

# 3. Template name priority list for rendering
template_names = ("row-mydb-mytable.html", "row.html")
```

### `datasette.views.row.RowView.data` · *method*

## Summary
Retrieves and prepares data for a specific table row, including metadata, display formatting, and foreign key relationships for rendering in templates.

## Description
This method handles the retrieval and preparation of data for a single row in a database table. It performs permission checks, executes a database query to fetch the row based on primary key values, formats the data for display, and prepares template data for rendering. The method is part of the RowView class which is responsible for displaying individual records.

The method is called during the data fetching phase of a web request to display a specific table row. It ensures proper authorization, retrieves the requested record, formats it for display purposes, and prepares additional metadata needed for template rendering.

## Args
- request: ASGI request object containing URL variables and query parameters
- default_labels: Boolean flag (default False) - currently unused in the implementation

## Returns
A tuple containing:
1. data (dict): Core data structure with database info, row data, columns, primary keys, and units
2. template_data (async function): Async function that returns template-specific data including display columns, display rows, foreign key tables, and metadata
3. template_names (tuple): Tuple of suggested template names for rendering the row

## Raises
- Forbidden: When the user lacks permission to view the requested table
- NotFound: When the database doesn't exist or the record with specified primary keys is not found

## State Changes
- Attributes READ: self.ds (datasette instance), self.ds.metadata(), self.ds.table_metadata()
- Attributes WRITTEN: None (method is read-only)

## Constraints
- Preconditions: 
  - Request must contain valid database, table, and pks URL variables
  - User must have appropriate permissions to view the table/database
  - Primary key values must uniquely identify a single row
- Postconditions:
  - If successful, returns properly formatted data and template data functions
  - If record not found, raises NotFound exception
  - If insufficient permissions, raises Forbidden exception

## Side Effects
- Database queries to retrieve row data and foreign key counts
- Template data preparation involving async operations
- Potential I/O operations for database connections

### `datasette.views.row.RowView.foreign_key_tables` · *method*

## Summary:
Retrieves related tables that reference the current table via foreign keys, including count statistics and navigation links.

## Description:
This method identifies all tables that have incoming foreign key references to the current table. For each such relationship, it calculates the number of referencing records and generates a navigation link to view those records. This functionality is used to display related data in the row view interface, allowing users to easily navigate from a record to related records in other tables.

The method is called from the `data` method of the `RowView` class when rendering row details, specifically to populate the `foreign_key_tables` context variable for templates.

## Args:
    database (str): Name of the database containing the table
    table (str): Name of the table being viewed
    pk_values (list[str]): List of primary key values for the current record (should contain exactly one value)

## Returns:
    list[dict]: List of dictionaries containing foreign key information with the following keys:
        - other_table (str): Name of the referencing table
        - other_column (str): Name of the foreign key column
        - column (str): Name of the referenced column in the current table
        - count (int): Number of records in the referencing table that reference this record
        - link (str): URL to view records in the referencing table filtered by this record's primary key

## Raises:
    QueryInterrupted: Raised when database query execution is interrupted, handled internally by returning empty list

## State Changes:
    Attributes READ: self.ds (Datasette instance)
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - pk_values must contain exactly one value (length must equal 1)
        - Database and table must exist and be accessible
        - The current table must have incoming foreign key relationships defined
    
    Postconditions:
        - Returns empty list when pk_values length is not 1
        - Returns empty list when no incoming foreign keys exist
        - Returns list of dictionaries with consistent structure when foreign keys exist

## Side Effects:
    - Executes database queries to count referencing records
    - Makes calls to self.ds.urls.table() to generate navigation URLs
    - May raise QueryInterrupted during database execution (handled internally)

