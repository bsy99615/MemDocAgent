# `renderer.py`

## `datasette.renderer.convert_specific_columns_to_json` · *function*

## Summary:
Converts specified JSON string columns in a list of rows to native Python objects.

## Description:
Processes a list of data rows and converts values in designated columns from JSON strings to native Python objects using `json.loads()`. This function is designed to handle cases where JSON data is stored as strings in database results but needs to be parsed for further processing or serialization. The function efficiently skips conversion for columns that don't require parsing.

## Args:
    rows (list[list]): A list of rows, where each row is a list of column values.
    columns (list[str]): A list of column names corresponding to the values in each row.
    json_cols (list[str]): A list of column names that should have their values converted from JSON strings to Python objects.

## Returns:
    list[list]: A new list of rows with specified JSON columns converted to Python objects. If no columns need conversion, the original rows are returned unchanged.

## Raises:
    None explicitly raised, though `json.loads()` may raise `TypeError` or `ValueError` internally which are caught and ignored.

## Constraints:
    Preconditions:
        - `rows` must be iterable and contain lists of equal length
        - `columns` must be the same length as each row in `rows`
        - `json_cols` must be iterable containing column names
    Postconditions:
        - The returned list contains the same number of rows as input
        - Columns not in `json_cols` remain unchanged
        - Columns in `json_cols` that can be parsed as JSON are converted to Python objects
        - Invalid JSON strings are left as-is (no conversion occurs)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start convert_specific_columns_to_json] --> B{Are any json_cols in columns?}
    B -- No --> C[Return original rows]
    B -- Yes --> D[Initialize new_rows]
    D --> E[For each row in rows]
    E --> F[For each value,column in zip(row, columns)]
    F --> G{Is column in json_cols?}
    G -- No --> H[Append value to new_row]
    G -- Yes --> I[Try json.loads(value)]
    I --> J{json.loads succeeds?}
    J -- No --> K[Pass (keep original value)]
    J -- Yes --> L[Replace value with parsed result]
    H --> M[Append new_row to new_rows]
    L --> M
    K --> M
    M --> N[Return new_rows]
```

## Examples:
    Example 1: Converting a single JSON column
    ```python
    rows = [['id', 'data'], [1, '{"key": "value"}']]
    columns = ['id', 'data']
    json_cols = ['data']
    result = convert_specific_columns_to_json(rows, columns, json_cols)
    # Returns: [['id', 'data'], [1, {'key': 'value'}]]
    ```

    Example 2: No conversion needed
    ```python
    rows = [['id', 'name'], [1, 'Alice']]
    columns = ['id', 'name']
    json_cols = ['data']
    result = convert_specific_columns_to_json(rows, columns, json_cols)
    # Returns: [['id', 'name'], [1, 'Alice']]
    ```

    Example 3: Multiple JSON columns with invalid JSON
    ```python
    rows = [['id', 'data1', 'data2'], [1, '{"key": "value"}', 'invalid-json']]
    columns = ['id', 'data1', 'data2']
    json_cols = ['data1', 'data2']
    result = convert_specific_columns_to_json(rows, columns, json_cols)
    # Returns: [['id', 'data1', 'data2'], [1, {'key': 'value'}, 'invalid-json']]
    # Note: data2 remains as string because it's not valid JSON
    ```

## `datasette.renderer.json_renderer` · *function*

## Summary:
Renders datasette query results as JSON with configurable shapes and formatting options.

## Description:
Transforms raw database query data into JSON format with various presentation options. This function handles the conversion of database rows into different JSON structures based on query parameters, including support for JSON column parsing, infinite value removal, and multiple output shapes (arrays, objects, etc.). It serves as the core rendering engine for JSON API responses in Datasette.

## Args:
    args (dict-like): Query arguments containing formatting parameters like `_shape`, `_json`, `_json_infinity`, and `_nl`
    data (dict): Raw query results containing rows, columns, and metadata
    view_name (str): Name of the view being rendered (used for debugging/tracing)

## Returns:
    Response: ASGI Response object containing properly formatted JSON data with appropriate HTTP status codes and headers

## Raises:
    None explicitly raised, though underlying functions may raise exceptions during JSON processing

## Constraints:
    Preconditions:
        - `args` must be a dictionary-like object with get() and getlist() methods
        - `data` must contain at least the basic structure expected by the renderer
        - `view_name` should be a valid string identifier for the view
    Postconditions:
        - Returns a properly formatted Response object with correct content type and status code
        - Data is serialized according to the specified shape parameter
        - Appropriate HTTP status codes are set for error conditions

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start json_renderer] --> B{Has _json param?}
    B -- Yes --> C[Get json_cols list]
    C --> D{json_cols and rows/columns exist?}
    D -- Yes --> E[Convert specific columns to JSON]
    E --> F[Remove infinite values if enabled]
    F --> G[Get _shape parameter]
    G --> H{Data has error?}
    H -- Yes --> I[Force shape to arrays]
    I --> J[Process shape selection]
    J --> K{shape == "arrayfirst"?}
    K -- Yes --> L[Extract first element of each row]
    L --> M[End]
    K -- No --> N{shape in ("objects", "object", "array")?}
    N -- Yes --> O[Process object/array transformations]
    O --> P{shape == "object"?}
    P -- Yes --> Q[Validate primary keys]
    Q --> R{Primary key validation failed?}
    R -- Yes --> S[Return error response]
    S --> T[End]
    R -- No --> U[Build object mapping by PK]
    U --> V[End]
    P -- No --> W[Return rows as-is]
    W --> V
    N -- No --> X{shape == "arrays"?}
    X -- Yes --> Y[No-op, continue]
    Y --> Z[End]
    X -- No --> AA[Set 400 status and error message]
    AA --> Z
```

## Examples:
    Basic array output:
    ```python
    args = {}
    data = {"rows": [[1, "Alice"], [2, "Bob"]], "columns": ["id", "name"]}
    response = json_renderer(args, data, "table_view")
    # Returns JSON: [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    ```

    Object shape with primary keys:
    ```python
    args = {"_shape": "object"}
    data = {
        "rows": [[1, "Alice"], [2, "Bob"]],
        "columns": ["id", "name"],
        "primary_keys": ["id"]
    }
    response = json_renderer(args, data, "table_view")
    # Returns JSON: {"1": {"id": 1, "name": "Alice"}, "2": {"id": 2, "name": "Bob"}}
    ```

    JSON column parsing:
    ```python
    args = {"_json": ["metadata"]}
    data = {
        "rows": [[1, '{"key": "value"}'], [2, '{"other": "data"}']],
        "columns": ["id", "metadata"]
    }
    response = json_renderer(args, data, "table_view")
    # Returns JSON with parsed metadata objects
    ```

