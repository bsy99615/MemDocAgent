# `blob_renderer.py`

## `datasette.blob_renderer.render_blob` · *function*

## Summary:
Renders binary blob data from a database table as a downloadable file with optional hash validation.

## Description:
This function handles the HTTP response for serving binary data stored in a database column. It validates the request parameters, optionally verifies the blob content against a provided hash, constructs a filename based on table and column identifiers, and returns the binary data as a downloadable file with appropriate headers.

## Args:
    datasette (Datasette): The Datasette instance providing access to the application context.
    database (str): Name of the database containing the table with blob data.
    rows (list[dict]): List of database rows returned by the query.
    columns (list[str]): List of column names available in the query results.
    request (Request): ASGI request object containing URL parameters and variables.
    table (str or None): Name of the table being queried, used for filename construction.
    view_name (str): Name of the view being rendered, used for filename construction.

## Returns:
    Response: An ASGI Response object containing the binary blob data with appropriate headers for file download.

## Raises:
    BadRequest: When required query parameters are missing or invalid, or when the blob hash doesn't match any row.

## Constraints:
    Preconditions:
        - The request must contain the `_BLOB_COLUMN` parameter.
        - The specified blob column must exist in the columns list.
        - If `_BLOB_HASH` is provided, it must correspond to one of the blob values in the rows.
    Postconditions:
        - Returns a Response object with status 200 and proper Content-Disposition header.
        - The response body contains the binary blob data or empty bytes if the value is None.

## Side Effects:
    - None

## Control Flow:
```mermaid
flowchart TD
    A[Start render_blob] --> B{Has _BLOB_COLUMN?}
    B -- No --> C[Raise BadRequest]
    B -- Yes --> D[Get blob_column]
    D --> E{blob_column in columns?}
    E -- No --> F[Raise BadRequest]
    E -- Yes --> G{Has _BLOB_HASH?}
    G -- Yes --> H[Get blob_hash]
    H --> I[Iterate rows]
    I --> J{SHA256 matches blob_hash?}
    J -- No --> K[Continue iteration]
    J -- Yes --> L[Break loop]
    K --> I
    L --> M{Found match?}
    M -- No --> N[Raise BadRequest]
    M -- Yes --> O[Set row]
    G -- No --> P[Set row = rows[0]]
    O --> Q[Get value from row]
    Q --> R[Construct filename]
    R --> S[Build headers]
    S --> T[Return Response]
```

## Examples:
```python
# Basic usage - serves first row's blob data
# Request: GET /database/table?_blob_column=blob_data
# Response: 200 OK with binary data and Content-Disposition header

# Hash-validated usage - serves specific blob matching hash
# Request: GET /database/table?_blob_column=blob_data&_blob_hash=abc123def456...
# Response: 200 OK with binary data if hash matches, BadRequest if not found
```

## `datasette.blob_renderer.register_output_renderer` · *function*

## Summary:
Registers a blob output renderer configuration that maps the ".blob" extension to the render_blob function with a disabled rendering condition.

## Description:
This function creates and returns a dictionary configuration that registers a custom output renderer for handling binary blob data in Datasette. The renderer is configured to handle files with the ".blob" extension, delegating the actual rendering to the render_blob function. The can_render condition is set to always return False, effectively disabling automatic rendering while keeping the configuration available for explicit use.

## Args:
    None

## Returns:
    dict: A configuration dictionary with three keys:
        - "extension" (str): File extension string "blob"
        - "render" (function): Reference to the render_blob function
        - "can_render" (callable): Lambda function that always returns False

## Raises:
    None

## Constraints:
    Preconditions:
        - The render_blob function must be defined in the same module
        - The function should be called during Datasette plugin initialization
    Postconditions:
        - Returns a dictionary with exact key-value structure as described
        - The can_render lambda function will always return False

## Side Effects:
    - None

## Control Flow:
```mermaid
flowchart TD
    A[Start register_output_renderer] --> B[Return config dict]
    B --> C{"extension": "blob"}
    B --> D{"render": render_blob}
    B --> E{"can_render": lambda: False}
```

## Examples:
```python
# Typical usage during plugin setup
renderer_config = register_output_renderer()
# Result: {"extension": "blob", "render": <function render_blob>, "can_render": <lambda>}
```

