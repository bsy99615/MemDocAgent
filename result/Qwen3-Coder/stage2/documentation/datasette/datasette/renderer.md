# `renderer.py`

## `datasette.renderer.convert_specific_columns_to_json` · *function*

## Summary:
Converts specified columns in dataset rows from JSON string representations to parsed Python objects.

## Description:
Processes a collection of rows and converts values in specific columns from JSON string format to their native Python data types (dict, list, int, float, bool, None). This function is particularly useful when JSON data is stored as strings in database columns but needs to be parsed for proper data manipulation or API responses. The function safely handles malformed JSON by preserving the original string value when parsing fails.

## Args:
    rows (list[list]): A list of rows, where each row is a list of column values
    columns (list[str]): A list of column names corresponding to the values in each row
    json_cols (list[str] or set[str]): A list or set of column names that should have their values converted from JSON strings to Python objects

## Returns:
    list[list]: A new list of rows with specified JSON columns converted to Python objects. If no columns need conversion (no intersection between json_cols and columns), returns the original rows unchanged.

## Raises:
    None explicitly raised - exceptions during JSON parsing are caught and ignored

## Constraints:
    Preconditions:
    - rows should be a list of lists where inner lists have the same length as columns
    - columns should be a list of strings with the same length as each row
    - json_cols should be iterable containing column names to convert
    
    Postconditions:
    - Returns a new list structure without modifying the original rows
    - Columns not in json_cols remain unchanged
    - JSON parsing errors result in the original string value being preserved
    - The function converts json_cols to a set internally for efficient lookup

## Side Effects:
    None - This function is pure and doesn't modify external state or perform I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[Start convert_specific_columns_to_json] --> B{Are any json_cols in columns?}
    B -- No --> C[Return original rows]
    B -- Yes --> D[Convert json_cols to set for efficient lookup]
    D --> E[Initialize new_rows]
    E --> F[For each row in rows]
    F --> G[Initialize new_row]
    G --> H[For each value,column in zip(row, columns)]
    H --> I{Is column in json_cols?}
    I -- No --> J[Append value to new_row]
    I -- Yes --> K[Try json.loads(value)]
    K --> L{json.loads succeeds?}
    L -- No --> M[Pass (preserve original value)]
    L -- Yes --> N[Replace value with parsed result]
    M --> O[Append value to new_row]
    N --> O
    O --> P[Append new_row to new_rows]
    P --> Q[Return new_rows]
```

## Examples:
    # Basic usage with simple JSON
    rows = [['{"name": "John"}', '25'], ['{"name": "Jane"}', '30']]
    columns = ['data', 'age']
    json_cols = ['data']
    result = convert_specific_columns_to_json(rows, columns, json_cols)
    # Returns: [[{'name': 'John'}, '25'], [{'name': 'Jane'}, '30']]
    
    # Mixed data with invalid JSON - original values preserved
    rows = [['{"valid": true}', '{"invalid":'], ['null', '42']]
    columns = ['col1', 'col2']
    json_cols = ['col1', 'col2']
    result = convert_specific_columns_to_json(rows, columns, json_cols)
    # Returns: [[{'valid': True}, '{"invalid":'], [None, '42']]
    
    # No conversion needed - returns original rows
    rows = [['{"name": "John"}', '25'], ['{"name": "Jane"}', '30']]
    columns = ['data', 'age']
    json_cols = ['other_col']
    result = convert_specific_columns_to_json(rows, columns, json_cols)
    # Returns: [['{"name": "John"}', '25'], ['{"name": "Jane"}', '30']]
    
    # Empty json_cols - returns original rows
    rows = [['{"name": "John"}', '25'], ['{"name": "Jane"}', '30']]
    columns = ['data', 'age']
    json_cols = []
    result = convert_specific_columns_to_json(rows, columns, json_cols)
    # Returns: [['{"name": "John"}', '25'], ['{"name": "Jane"}', '30']]
```

## `datasette.renderer.json_renderer` · *function*

## Summary:
Renders dataset query results as JSON with configurable formatting options and data transformations.

## Description:
Processes raw dataset query data and transforms it into JSON format according to various query parameters. This function serves as the core JSON rendering engine for Datasette, supporting multiple output shapes, JSON column parsing, infinity handling, and newline-delimited output formats.

The function handles several query parameters:
- `_json`: Specifies which columns should have their values parsed from JSON strings to Python objects
- `_json_infinity`: Controls whether infinite values are removed from results
- `_shape`: Determines the output structure (arrays, objects, arrayfirst, etc.)
- `_nl`: Enables newline-delimited JSON output for array shapes

This logic is extracted into its own function to separate the concerns of data transformation from the view layer, allowing for consistent JSON rendering across different dataset views while maintaining clean separation of responsibilities.

## Args:
    args (dict-like): Query parameters from the HTTP request
        - `_json` (optional): Column names to parse as JSON strings
        - `_json_infinity` (optional): Boolean flag to control infinity removal (default: "0")
        - `_shape` (optional): Output shape format (default: "arrays")
        - `_nl` (optional): Newline delimiter flag for array output
    data (dict): Raw dataset query results containing:
        - `rows` (list): Query result rows
        - `columns` (list): Column names for the rows
        - `primary_keys` (list, optional): Primary key definitions for object shape
        - `error` (str, optional): Error message if query failed
        - `next_url` (str, optional): URL for pagination
    view_name (str): Name of the view being rendered (used for routing decisions and view-specific behavior)

## Returns:
    Response: ASGI Response object containing properly formatted JSON data with appropriate HTTP status codes and headers

## Raises:
    None explicitly raised - all errors are handled by returning appropriate error responses with status codes

## Constraints:
    Preconditions:
    - `data` must contain either `rows` and `columns` or an `error` field
    - `args` must be a dictionary-like object with get() and getlist() methods
    - When using `_shape=object`, `data` must contain `primary_keys` field
    
    Postconditions:
    - Returns a Response object with valid JSON body
    - Appropriate HTTP status codes are set (200 for success, 400 for invalid parameters)
    - Headers include link header for pagination when applicable

## Side Effects:
    - May perform JSON parsing on specified columns (in-memory operations)
    - May remove infinite values from numeric fields (in-memory operations)
    - Sets HTTP headers including 'link' for pagination
    - Returns ASGI Response object with JSON content

## Control Flow:
```mermaid
flowchart TD
    A[Start json_renderer] --> B{Has _json param?}
    B -- Yes --> C[Get json_cols list]
    C --> D{json_cols and rows/columns exist?}
    D -- Yes --> E[Convert specific columns to JSON]
    E --> F[Remove infinites if enabled]
    F --> G[Get _shape parameter]
    G --> H{Has error in data?}
    H -- Yes --> I[Force shape to arrays]
    I --> J[Process shape]
    H -- No --> J
    J --> K{shape == "arrayfirst"?}
    K -- Yes --> L[Extract first element of each row]
    K -- No --> M{shape in ("objects", "object", "array")?}
    M -- Yes --> N[Process object/array transformations]
    N --> O{shape == "object"?}
    O -- Yes --> P{Has primary_keys?}
    P -- No --> Q[Set error for missing primary_keys]
    P -- Yes --> R{Empty primary_keys?}
    R -- Yes --> S[Set error for no primary_keys]
    R -- No --> T[Build object_rows with PK-based keys]
    T --> U[Set data to object_rows]
    Q --> V[Set error in data]
    S --> V
    V --> W[Set data to error response]
    O -- No --> X[Set data to rows]
    M -- No --> Y{shape == "arrays"?}
    Y -- Yes --> Z[Do nothing]
    Y -- No --> AA[Set 400 status and error response]
    Z --> AB[Prepare body and content_type]
    AA --> AB
    AB --> AC{Has _nl and shape=array?}
    AC -- Yes --> AD[Use newline-delimited JSON]
    AC -- No --> AE[Use standard JSON]
    AD --> AF[Set content_type=text/plain]
    AE --> AF
    AF --> AG[Set headers with link if next_url exists]
    AG --> AH[Return Response]
```

## Examples:
    # Basic array output
    args = {"_shape": "arrays"}
    data = {"rows": [[1, "Alice"], [2, "Bob"]], "columns": ["id", "name"]}
    response = json_renderer(args, data, "table_view")
    # Returns JSON: {"rows": [[1, "Alice"], [2, "Bob"]], "columns": ["id", "name"]}

    # Object shape with primary keys
    args = {"_shape": "object"}
    data = {
        "rows": [[1, "Alice"], [2, "Bob"]], 
        "columns": ["id", "name"],
        "primary_keys": ["id"]
    }
    response = json_renderer(args, data, "table_view")
    # Returns JSON: {"1": [1, "Alice"], "2": [2, "Bob"]}

    # Array-first shape
    args = {"_shape": "arrayfirst"}
    data = {"rows": [["Alice"], ["Bob"]], "columns": ["name"]}
    response = json_renderer(args, data, "table_view")
    # Returns JSON: ["Alice", "Bob"]

    # JSON parsing of specific columns
    args = {"_json": ["metadata"], "_shape": "arrays"}
    data = {
        "rows": [['{"active": true}', "2023-01-01"], ['{"active": false}', "2023-01-02"]], 
        "columns": ["metadata", "date"]
    }
    response = json_renderer(args, data, "table_view")
    # Returns JSON with parsed metadata objects

