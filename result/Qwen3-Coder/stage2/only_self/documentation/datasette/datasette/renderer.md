# `renderer.py`

## `datasette.renderer.convert_specific_columns_to_json` · *function*

## Summary:
Converts specified columns from JSON string representations to Python objects in a collection of rows.

## Description:
Processes a list of rows and converts values in designated columns from JSON strings to their native Python objects using json.loads(). This function is designed to handle potentially malformed JSON data gracefully by catching parsing errors and leaving invalid values unchanged.

## Args:
    rows (list[list]): A list of rows, where each row is a list of column values in the same order as the columns parameter.
    columns (list[str]): A list of column names corresponding to the order of values in each row.
    json_cols (list[str]): A list of column names that should have their values converted from JSON strings to Python objects.

## Returns:
    list[list]: A new list of rows with specified JSON columns converted to Python objects. If no columns intersect between json_cols and columns, the original rows are returned unchanged.

## Raises:
    None explicitly raised. Parsing errors are caught and ignored.

## Constraints:
    Preconditions:
        - rows must be iterable containing lists of equal length
        - columns must be a list of strings matching the row structure
        - json_cols must be iterable of strings
    
    Postconditions:
        - Returned rows maintain the same structure as input rows
        - Non-JSON columns remain unchanged
        - JSON columns with valid JSON strings are converted to Python objects
        - JSON columns with invalid JSON strings retain their original string values

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start convert_specific_columns_to_json] --> B{json_cols ∩ columns ≠ ∅?}
    B -- No --> C[Return original rows]
    B -- Yes --> D[Initialize new_rows]
    D --> E[For each row in rows]
    E --> F[Initialize new_row]
    F --> G[For each (value, column) in zip(row, columns)]
    G --> H{column in json_cols?}
    H -- No --> I[Append value to new_row]
    H -- Yes --> J[Try json.loads(value)]
    J --> K{json.loads succeeds?}
    K -- No --> L[Pass (keep original value)]
    K -- Yes --> M[Append parsed value to new_row]
    L --> N[Append value to new_row]
    N --> O[Append new_row to new_rows]
    M --> O
    O --> P[Return new_rows]
```

## Examples:
    # Basic usage with valid JSON
    rows = [['{"a": 1}', 'text'], ['{"b": 2}', 'more']]
    columns = ['json_col', 'text_col']
    json_cols = ['json_col']
    result = convert_specific_columns_to_json(rows, columns, json_cols)
    # Returns: [[{'a': 1}, 'text'], [{'b': 2}, 'more']]
    
    # Usage with invalid JSON (no change)
    rows = [['invalid_json', 'text'], ['{"valid": true}', 'more']]
    columns = ['json_col', 'text_col']
    json_cols = ['json_col']
    result = convert_specific_columns_to_json(rows, columns, json_cols)
    # Returns: [['invalid_json', 'text'], [{'valid': True}, 'more']]
    
    # No intersection case (returns original)
    rows = [['data1', 'data2']]
    columns = ['col1', 'col2']
    json_cols = ['nonexistent']
    result = convert_specific_columns_to_json(rows, columns, json_cols)
    # Returns: [['data1', 'data2']]

## `datasette.renderer.json_renderer` · *function*

## Summary:
Renders datasette query results as JSON with configurable formatting options including shape transformations, JSON column handling, and infinity filtering.

## Description:
Processes raw datasette query data and transforms it into JSON format with various output shapes and formatting options. This function serves as the core JSON renderer for Datasette's API endpoints, supporting multiple output formats through URL parameters and handling special data transformations like JSON column parsing and infinity value removal.

## Args:
    args (dict-like): Query arguments containing formatting parameters such as:
        - "_json": List of column names to convert from JSON strings to Python objects
        - "_json_infinity": String representation of boolean flag to enable/disable infinity value removal (default: "0")
        - "_shape": Output shape format ("arrays", "arrayfirst", "objects", "object", "array") 
        - "_nl": Newline delimiter flag for array output
    data (dict): Raw query results containing:
        - "rows": List of row data (list of lists or list of dicts)
        - "columns": Column names for the rows
        - "primary_keys": Primary key definitions (for object shape)
        - "error": Error message if query failed
        - "next_url": Pagination URL for next page
        - "view_name": Name of the view being rendered (used for routing decisions)
    view_name (str): Name of the view being rendered (used for routing decisions)

## Returns:
    Response: ASGI Response object containing JSON-formatted data with appropriate HTTP status code and headers

## Raises:
    None explicitly raised. Invalid shape parameters result in a 400 status code with error details in the response body.

## Constraints:
    Preconditions:
        - args must be a dictionary-like object with get() and getlist() methods
        - data must contain at least "rows" and "columns" keys when processing rows
        - When using "_shape=object", data must contain "primary_keys" key
        - When using "_shape=object", data must have non-empty primary_keys for valid transformation
        - Rows must be iterable with consistent structure

    Postconditions:
        - Returns a Response object with proper JSON content
        - Data transformation follows specified shape parameter
        - Error responses have appropriate HTTP status codes (400 for invalid shapes)
        - Infinity values are filtered out when _json_infinity is truthy
        - JSON columns are parsed when _json parameter is provided

## Side Effects:
    - May perform JSON parsing on specified columns (via convert_specific_columns_to_json)
    - May filter out infinity values (via remove_infinites)
    - Adds Link header to response when next_url is present

## Control Flow:
```mermaid
flowchart TD
    A[Start json_renderer] --> B{Has _json param?}
    B -- Yes --> C[Get json_cols list using getlist()]
    C --> D{json_cols and rows/columns exist?}
    D -- Yes --> E[Convert specific columns to JSON]
    E --> F[Remove infinities if _json_infinity is falsy]
    F --> G[Get _shape parameter]
    G --> H{Data has error?}
    H -- Yes --> I[Force shape to "arrays"]
    I --> J[Process shape]
    H -- No --> J
    J --> K{shape == "arrayfirst"?}
    K -- Yes --> L[Extract first element of each row]
    K -- No --> M{shape in ("objects", "object", "array")?}
    M -- Yes --> N[Transform rows to dicts with column names]
    N --> O{shape == "object"?}
    O -- Yes --> P{Has primary_keys?}
    P -- No --> Q[Set error message]
    P -- Yes --> R{Has empty primary_keys?}
    R -- Yes --> Q
    R -- No --> S[Build object_rows with PK paths]
    S --> T[Return object_rows]
    Q --> U[Set error response]
    U --> V[Return error response]
    O -- No --> W[Return rows as-is]
    M -- No --> X{shape == "arrays"?}
    X -- Yes --> Y[No-op]
    X -- No --> Z[Set 400 status and error message]
    Z --> AA[Return error response]
    Y --> AB[Continue to NL processing]
    W --> AB
    AB --> AC{Has _nl and shape == "array"?}
    AC -- Yes --> AD[Join with newlines]
    AC -- No --> AE[Standard JSON dump]
    AD --> AF[Set content-type to text/plain]
    AE --> AF
    AF --> AG[Add link header if next_url exists]
    AG --> AH[Return Response]
```

## Examples:
    # Basic array output
    args = {"_shape": "arrays"}
    data = {"rows": [[1, "test"], [2, "data"]], "columns": ["id", "name"]}
    response = json_renderer(args, data, "table_view")
    # Returns JSON: {"rows": [[1, "test"], [2, "data"]]}

    # Object shape with primary keys
    args = {"_shape": "object"}
    data = {
        "rows": [{"id": 1, "name": "test"}, {"id": 2, "name": "data"}],
        "columns": ["id", "name"],
        "primary_keys": ["id"]
    }
    response = json_renderer(args, data, "table_view")
    # Returns JSON: {"1": {"id": 1, "name": "test"}, "2": {"id": 2, "name": "data"}}

    # Array with JSON column conversion
    args = {"_json": ["metadata"], "_shape": "arrays"}
    data = {
        "rows": [["{\"key\": \"value\"}", "text"], ["{\"other\": 123}", "more"]],
        "columns": ["metadata", "content"]
    }
    response = json_renderer(args, data, "table_view")
    # Returns JSON: {"rows": [{"key": "value"}, "text"], [{"other": 123}, "more"]}

    # Error case with invalid shape
    args = {"_shape": "invalid_shape"}
    data = {"error": "Query failed"}
    response = json_renderer(args, data, "table_view")
    # Returns JSON: {"ok": false, "error": "Invalid _shape: invalid_shape", "status": 400}

