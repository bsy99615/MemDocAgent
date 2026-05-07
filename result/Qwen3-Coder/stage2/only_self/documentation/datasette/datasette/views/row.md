# `row.py`

## `datasette.views.row.RowView` · *class*

## Summary:
RowView handles displaying individual record data from a database table in Datasette, providing detailed row information with optional foreign key table counts.

## Description:
The RowView class is responsible for retrieving and formatting a single record from a database table based on primary key values. It performs permission checks, fetches the requested row data, and prepares it for rendering in templates. The class also provides additional metadata including foreign key relationships and table-specific configurations.

This class is typically instantiated by Datasette's routing system when handling requests to view individual records (e.g., `/database/table/pk_values`). It serves as the backend handler for the "row" view type in Datasette's web interface.

## State:
- `name` (str): Class attribute identifying this view type as "row"
- `ds`: Datasette instance providing access to databases, permissions, and configuration
- All attributes inherited from DataView parent class

## Lifecycle:
- Creation: Instantiated automatically by Datasette's routing system when handling row view requests
- Usage: Called via `data()` method which processes HTTP requests and returns data for rendering
- Destruction: No explicit cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
flowchart TD
    A[Request received] --> B[data()]
    B --> C{Permission check}
    C -->|Denied| D[Forbidden exception]
    C -->|Allowed| E[Parse PK values]
    E --> F[Get database]
    F --> G[Execute SQL query]
    G --> H{Row found?}
    H -->|No| I[NotFound exception]
    H -->|Yes| J[Prepare template data]
    J --> K[Return data tuple]
    K --> L[Template rendering]
    
    M[data()] --> N[foreign_key_tables()]
    N --> O[Check PK count]
    O -->|Not 1| P[Return empty list]
    P --> Q[Get foreign keys]
    Q --> R[Build SQL query]
    R --> S[Execute query]
    S --> T[Process results]
    T --> U[Return foreign key tables]
```

## Raises:
- `Forbidden`: Raised when user lacks permission to view the requested table or database
- `NotFound`: Raised when the requested database is not found or when the record with specified primary keys does not exist
- `QueryInterrupted`: Raised internally when database query execution is interrupted (caught and handled gracefully)

## Example:
```python
# Typical usage would be triggered by Datasette routing:
# GET /mydb/mytable/123

# The data() method returns a tuple of:
# 1. Data dictionary containing row information
# 2. Async template_data function for rendering
# 3. Tuple of template name suggestions

# Example return structure:
(
    {
        "database": "mydb",
        "table": "mytable", 
        "rows": [[123, "John", "Doe"]],
        "columns": ["id", "first_name", "last_name"],
        "primary_keys": ["id"],
        "primary_key_values": ["123"],
        "units": {},
        "foreign_key_tables": [
            {
                "other_table": "orders",
                "other_column": "customer_id",
                "count": 5,
                "link": "/mydb/orders?customer_id=123"
            }
        ]
    },
    async_function,  # template_data function
    ("row-mydb-mytable.html", "row.html")  # template name suggestions
)
```

### `datasette.views.row.RowView.data` · *method*

## Summary:
Retrieves and prepares data for a specific row in a database table, including permission checking and template preparation.

## Description:
This asynchronous method handles the retrieval of a single row from a database table based on primary key values provided in the request URL. It performs permission validation, executes a database query to fetch the row data, processes the results for display, and prepares template data for rendering. The method is designed to be called as part of the row view lifecycle in Datasette's web interface.

## Args:
    request: ASGI request object containing URL variables and query parameters
    default_labels: Boolean flag (default False) for controlling label behavior in display

## Returns:
    tuple: A 3-tuple containing:
        - data (dict): Core data including database name, table name, rows, columns, primary keys, primary key values, and units
        - template_data (async function): Async function that returns template-specific data including display columns, display rows, foreign key tables, custom table templates, and metadata
        - template_names (tuple): Tuple of suggested template names for rendering the row view, in order of preference

## Raises:
    NotFound: When database is not found, or when the requested record does not exist
    Forbidden: When user lacks permission to view the requested table

## State Changes:
    Attributes READ: self.ds (datasette instance)
    Attributes WRITTEN: None (method is read-only)

## Constraints:
    Preconditions:
        - Request must contain valid database, table, and pks URL variables
        - User must have appropriate permissions to view the table
        - Primary key values must uniquely identify a single row
    Postconditions:
        - Returns properly formatted data structure for row display
        - Template data function is ready to be awaited for rendering

## Side Effects:
    - Database query execution
    - Permission checking via datasette instance
    - Template name construction using CSS class conversion

### `datasette.views.row.RowView.foreign_key_tables` · *method*

## Summary:
Retrieves related tables connected through foreign key relationships for a given database row.

## Description:
This method identifies all tables that have incoming foreign key references to the specified table, counts how many records in those tables reference the current row's primary key value, and generates links to view those related records. It's used to display "related tables" information on row detail pages.

## Args:
    database (str): Name of the database containing the table
    table (str): Name of the table being queried  
    pk_values (list[str]): List of primary key values for the current row (must contain exactly one value)

## Returns:
    list[dict]: List of dictionaries containing foreign key relationship information, each with:
        - All original foreign key metadata from the database schema
        - Additional "count" field indicating number of related records
        - Additional "link" field providing URL to view related records
        - Returns empty list when pk_values contains zero or multiple values, or when no incoming foreign keys exist

## Raises:
    None explicitly raised - handles QueryInterrupted internally by returning empty list

## State Changes:
    Attributes READ: self.ds (Datasette instance), self.ds.databases, self.ds.urls
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - pk_values must contain exactly one value (len(pk_values) == 1)
        - Database and table must exist and be accessible
        - Table must have incoming foreign key relationships
    Postconditions:
        - Returns empty list if pk_values length is not 1
        - Returns empty list if no incoming foreign keys exist
        - Returns list of dictionaries with consistent structure for each foreign key relationship

## Side Effects:
    - Executes database queries to count related records
    - May raise QueryInterrupted which is caught and handled by returning empty list

