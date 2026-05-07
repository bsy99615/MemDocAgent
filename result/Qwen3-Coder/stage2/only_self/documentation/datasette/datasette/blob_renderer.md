# `blob_renderer.py`

## `datasette.blob_renderer.render_blob` · *function*

## Summary:
Renders binary blob data from a database table as a downloadable file with optional hash validation.

## Description:
This asynchronous function retrieves binary data from a specified column in a database table and returns it as an HTTP response with appropriate headers for file download. It supports optional hash-based validation to ensure the requested content hasn't changed since the link was generated. The function is designed to be used as a Datasette plugin hook for serving binary content via the `datasette.blob_renderer` hook.

## Args:
    datasette (Datasette): The Datasette instance providing access to the application context
    database (str): Name of the database containing the table
    rows (list[dict]): List of database rows containing the blob data, where each dict maps column names to values
    columns (list[str]): List of column names available in the table
    request (Request): ASGI request object containing query parameters and URL variables
    table (str or None): Name of the table being queried, used for filename generation
    view_name (str): Name of the view being rendered, used for filename generation

## Returns:
    Response: An ASGI Response object containing the binary data with appropriate headers for file download. The response body contains the raw binary data from the specified blob column.

## Raises:
    BadRequest: When required query parameters are missing (`_BLOB_COLUMN` parameter), when an invalid column name is provided, or when hash validation fails due to mismatched content.

## Constraints:
    Preconditions:
    - The request must contain a `_BLOB_COLUMN` query parameter specifying which column contains the blob data
    - The specified column must exist in the columns list
    - If `_BLOB_HASH` is provided, it must match the SHA256 hash of one of the rows' blob data
    - The rows list must not be empty
    
    Postconditions:
    - Returns a Response object with status 200 and proper Content-Disposition header
    - Binary data is returned as the response body
    - The Content-Disposition header includes a filename based on table, primary keys, and column name

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
    G -- Yes --> H[Validate hash against rows]
    H --> I{Hash match found?}
    I -- No --> J[Raise BadRequest]
    I -- Yes --> K[Set row to matching row]
    G -- No --> L[Set row to rows[0]]
    K --> M[Get value from row[blob_column]]
    L --> M
    M --> N[Build filename]
    N --> O[Set headers]
    O --> P[Return Response with body, headers, and content-type]
```

## Examples:
```python
# Basic usage - returns first row's blob data as downloadable file
# URL: /database/table?_blob_column=blob_data

# Hash-validated usage - ensures content hasn't changed
# URL: /database/table?_blob_column=blob_data&_blob_hash=abc123def456...
```

## `datasette.blob_renderer.register_output_renderer` · *function*

## Summary:
Registers a blob output renderer configuration with Datasette for handling binary file downloads.

## Description:
This function serves as a hook implementation that returns a configuration dictionary for registering a blob output renderer with Datasette. The renderer is specifically designed to handle binary data from database tables and serve it as downloadable files. It's intended to be used as part of Datasette's plugin system through the `datasette.blob_renderer` hook.

## Args:
    None

## Returns:
    dict: A configuration dictionary with three keys:
        - "extension" (str): File extension this renderer handles ("blob")
        - "render" (function): The render function that processes blob data (render_blob)
        - "can_render" (callable): A lambda function that always returns False, indicating this renderer is not automatically selected for rendering

## Raises:
    None

## Constraints:
    Preconditions:
    - This function should only be called as part of Datasette's plugin initialization process
    - The `render_blob` function must be available in the same module scope
    
    Postconditions:
    - Returns a properly formatted configuration dictionary for Datasette's renderer system
    - The returned configuration is compatible with Datasette's hook implementation requirements

## Side Effects:
    - None

## Control Flow:
```mermaid
flowchart TD
    A[register_output_renderer called] --> B[Return configuration dict]
    B --> C["extension": "blob"]
    B --> D["render": render_blob]
    B --> E["can_render": lambda: False]
```

## Examples:
```python
# This function is typically used internally by Datasette plugins
# and would be called automatically during plugin initialization:

# Configuration returned:
{
    "extension": "blob",
    "render": render_blob,
    "can_render": lambda: False
}
```

