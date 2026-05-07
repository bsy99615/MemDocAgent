# `renderer.py`

## `datasette.renderer.convert_specific_columns_to_json` · *function*

block. Then I will self-verify and finish.

Action: WRITE
<DOCUMENTATION>
## Summary:
Parse JSON-encoded values in specific columns of a sequence of rows, returning a new list of rows with those values converted to Python objects while leaving other values unchanged.

## Description:
This function is intended to be used in a rendering or serialization pipeline where certain result columns contain JSON-encoded strings that should be converted into native Python objects (lists, dicts, numbers, booleans, etc.) prior to further processing or final output.

Known callers and context:
- Typically invoked by rendering logic that prepares database query rows for JSON output, i.e., when some columns are known to contain JSON text and need parsing before final JSON encoding. (No explicit caller function names were provided with the component; the function is designed for use in a renderer/response-preparation stage.)

Why this logic is extracted:
- Parsing selected columns is a discrete responsibility: identifying which columns require JSON decoding, applying decoding safely per-cell, and preserving other columns untouched. Extracting it avoids duplicating the same try/except decode pattern in multiple renderers and centralizes the behavior and edge-case handling (invalid JSON, non-string values).

## Args:
    rows (iterable[sequence]): Iterable of row sequences (e.g., list/tuple per row). Each row is expected to be an ordered sequence of column values aligned with `columns`. The function returns a list of lists derived from these rows.
    columns (sequence[str]): Sequence of column names in the same order as values appear in each row. Length should match the number of values of each row (see Preconditions).
    json_cols (iterable[str]): Iterable of column names that should be parsed as JSON. Values in columns whose name is in this set will be passed to json.loads.

Interdependencies:
- `columns` and each `row` must align in order (the function zips values with `columns`); misalignment may cause truncation of values (see Control Flow and Preconditions).

## Returns:
    list[list]: A new list of rows (each row is a list) where any value from columns listed in `json_cols` has been replaced with the result of json.loads(value) when parsing succeeds. For values that are not valid JSON or when json.loads raises TypeError/ValueError, the original value is left unchanged.

Special return behavior:
- If none of the `json_cols` names intersect with `columns`, the function returns the original `rows` object unchanged (same reference), performing no copying or per-row processing.

## Raises:
    This function does not raise exceptions on JSON parse failures: json.loads errors of type TypeError or ValueError are caught and the original cell value is preserved.
    It may raise exceptions if callers pass non-iterable arguments (e.g., passing None for `rows` or `columns`) or if iteration over `rows` itself raises—these are not explicitly handled by the function.

## Constraints:
Preconditions:
- `columns` is an ordered sequence of column names corresponding to values in each row.
- Each element in `rows` is an iterable (sequence) whose values are ordered to match `columns`. The function relies on zip(row, columns) — if row length and columns length differ, iteration will be truncated to the shorter length.
- `json_cols` is an iterable of column names; it will be converted to a set internally.

Postconditions:
- If processing occurs, the returned value is a newly constructed list of lists; for processed columns, JSON strings that parsed successfully are replaced by their Python representations.
- If no columns in `json_cols` match `columns`, the original `rows` object is returned unchanged.

## Side Effects:
- No I/O (files, network, stdout) is performed.
- No mutation of the input `rows` or its inner row objects is performed by the function: when parsing is required the function builds new row lists and returns them; if no parsing is required the original `rows` reference is returned.
- No external state is modified.

## Control Flow:
flowchart TD
    A[Start] --> B[Convert json_cols to set]
    B --> C{Any json_cols in columns?}
    C -- No --> D[Return original rows]
    C -- Yes --> E[Initialize new_rows = []]
    E --> F[For each row in rows]
    F --> G[Initialize new_row = []]
    G --> H[For each (value, column) in zip(row, columns)]
    H --> I{column in json_cols?}
    I -- No --> J[Append original value to new_row]
    I -- Yes --> K[Try json.loads(value)]
    K --> L{json.loads succeeded?}
    L -- Yes --> M[Append parsed value to new_row]
    L -- No --> N[Append original value to new_row]
    J --> O[Next (value, column)]
    M --> O
    N --> O
    O --> P[After all columns, append new_row to new_rows]
    P --> Q[Next row]
    Q --> R[After all rows, return new_rows]

## Examples:
1) Basic usage — successful parse:
    rows = [
        ("1", '{"a": 10}', "x"),
        ("2", '{"a": 20}', "y"),
    ]
    columns = ["id", "data", "tag"]
    json_cols = ["data"]
    result = convert_specific_columns_to_json(rows, columns, json_cols)
    # result -> [
    #   ["1", {"a": 10}, "x"],
    #   ["2", {"a": 20}, "y"],
    # ]

2) Invalid JSON stays unchanged:
    rows = [
        ("1", 'not a json', "x"),
    ]
    columns = ["id", "data", "tag"]
    json_cols = ["data"]
    result = convert_specific_columns_to_json(rows, columns, json_cols)
    # result -> [["1", "not a json", "x"]]

3) No matching json_cols -> identity return (same object):
    rows = [("1", "x")]
    columns = ["id", "tag"]
    json_cols = ["data"]
    result = convert_specific_columns_to_json(rows, columns, json_cols)
    # result is the same object as rows (no processing performed)

4) Note on alignment:
    If a row has more values than there are column names, or fewer, zip will stop at the shortest sequence; this function therefore expects callers to provide properly aligned rows and columns to avoid unintended truncation.

## `datasette.renderer.json_renderer` · *function*

## Summary:
Renders query/result data into a JSON (or newline-delimited JSON/plain-text) HTTP response, transforming rows according to request query parameters (_shape, _json, _json_infinity, _nl) and returning an ASGI Response with appropriate status, headers, and content type.

## Description:
This function is a serializer used at the HTTP response stage of a request handling pipeline to convert an internal "data" structure (often the result of a database query or table/view rendering) into a JSON-compatible HTTP response body and headers.

Known callers and context:
- Typically invoked by the web request handling / renderer dispatch layer that selects an output renderer based on the requested format (for example, when a client requests JSON or when programmatically rendering results). The caller passes request query parameters (args), the result payload (data), and a view identifier (view_name).
- It is expected to run after data has been collected and arranged into the common "data" dict shape used by the application (with keys such as "rows", "columns", "primary_keys", "error", "next_url").

Why this is extracted into a separate function:
- Separates rendering concerns (formatting, shape conversion, JSON encoding, headers) from data retrieval and business logic.
- Encapsulates all behavior related to query-parameter-driven JSON output (multiple _shape modes, JSON column decoding, infinity handling, newline-delimited output) in a single place so other parts of the code can remain format-agnostic.

## Args:
    args (mapping-like object):
        Type: dict-like / MultiDict-like object that implements get(key, default),
        getlist(key) for repeated parameters, and membership test ("_json" in args).
        Expected keys used:
            - "_json" (optional): may appear multiple times; getlist("_json") returns
              a list of column names whose values should be converted from JSON strings.
            - "_json_infinity" (optional): string flag; if truthy (value evaluated via
              value_as_boolean) allows Infinity/-Infinity/NaN to remain; default "0".
            - "_shape" (optional): one of "arrays" (default), "arrayfirst", "objects",
              "object", "array", or other (results in 400 error).
            - "_nl" (optional): if non-empty and shape == "array", render newline-delimited
              JSON lines and set content type to text/plain.
        Interdependencies:
            - getlist("_json") is only used when both "rows" and "columns" exist in data.
            - "_json_infinity" controls whether remove_infinites is applied to rows.

    data (dict):
        Type: dict-like payload representing the result to be rendered.
        Common keys:
            - "rows": list of row sequences (each row is a sequence/iterable of column values)
            - "columns": list of column names corresponding to row positions
            - "primary_keys": list of primary key column names (used by _shape=object)
            - "error": present if an earlier stage produced an error result (truthy)
            - "next_url": optional URL string used to populate a "Link: <...>; rel=\"next\"" header
        Notes:
            - If "error" is present/truthy, the function forces _shape to "arrays" regardless of args.
            - The function may replace/transform the data variable to other types (list, dict,
              or the original data dict containing rows/columns), depending on _shape.

    view_name (str):
        Type: string identifier of the view being rendered. This parameter is accepted
        but unused by this function (provided for renderer signature compatibility).

## Returns:
    datasette.utils.asgi.Response
    - body (str): JSON-encoded string (application/json; charset=utf-8) for most shapes,
      or newline-delimited JSON text/plain when _nl is set and shape == "array".
      Exact body contents depend on _shape:
        - _shape="arrays" (default): returns the original `data` dict JSON-encoded.
        - _shape="arrayfirst": returns JSON array of the first column values: [row[0], ...]
        - _shape in ("objects","object","array"):
            * When rows and columns are present, rows are first converted to objects
              (list of dicts mapping column->value).
            * _shape="array": returns that list of row objects (content-type still application/json)
            * _shape="objects": behaves like "array" (alias)
            * _shape="object": attempts to return an object mapping primary-key-string -> row-object;
              if requirements are not met, returns {"ok": False, "error": "..."} with status 200.
        - Invalid _shape: returns {"ok": False, "error": f"Invalid _shape: {shape}", "status":400, "title": None}
          and sets HTTP status to 400.
      When _nl is truthy and shape == "array", body is newline-separated JSON representations of each item
      (content-type "text/plain"); otherwise the entire response is a single JSON document.
    - status (int): 200 on success (or non-fatal shape-specific errors that are reported in the JSON body),
      400 when an invalid _shape was provided.
    - headers (dict): may include a "link" header when data["next_url"] is present with format
      '<{next_url}>; rel="next"'.
    - content_type (str): either "application/json; charset=utf-8" or "text/plain".

## Raises:
    The function does not raise exceptions itself in normal execution; it builds and returns a Response.
    Any exceptions exhibited will come from helper utilities it calls:
      - convert_specific_columns_to_json: if that helper raises, the exception will propagate.
      - remove_infinites: if that helper raises, the exception will propagate.
      - json.dumps(CustomJSONEncoder): if CustomJSONEncoder cannot encode a value, json.dumps may raise TypeError.
    No explicit exceptions (e.g., ValueError) are raised directly by this function.

## Constraints:
    Preconditions:
        - args must be a mapping-like object supporting membership test, get(key, default),
          and getlist(key) for repeated query parameters.
        - data must be a dict-like structure with expected keys for the chosen _shape:
            * For _shape modes that rely on rows and columns, both should be present and rows must be iterable.
            * For _shape="object", data should contain "primary_keys" with at least one entry for a successful object mapping.
    Postconditions:
        - The function always returns an instance of Response containing a serialized representation
          of the provided data (or an error object) and appropriate headers/content_type.
        - If an invalid _shape is provided, Response.status == 400 and the body contains an error object describing the invalid shape.

## Side Effects:
    - No persistent I/O, database writes, or global state mutation occur in this function.
    - Constructs and returns an HTTP Response object; may include a "link" header derived from data["next_url"].
    - Calls out to helper functions (convert_specific_columns_to_json, remove_infinites, path_from_row_pks, json.dumps with CustomJSONEncoder) which may perform their own side effects (not within this function's control).

## Control Flow:
flowchart TD
    A[Start: json_renderer(args, data, view_name)] --> B{"_json" in args?}
    B -->|yes| C[getlist("_json") -> json_cols]
    C --> D{data has "rows" and "columns"?}
    D -->|yes| E[call convert_specific_columns_to_json -> replace data["rows"]]
    D -->|no| F[skip JSON-column conversion]
    B -->|no| F
    F --> G{data has "rows" and _json_infinity false?}
    G -->|yes| H[replace each row with remove_infinites(row)]
    G -->|no| I[leave rows unchanged]
    H --> I
    I --> J[determine shape = args.get("_shape","arrays")]
    J --> K{data.get("error") truthy?}
    K -->|yes| L[force shape = "arrays"]
    K -->|no| M[use requested shape]
    L --> N{shape}
    M --> N
    N -->|arrayfirst| O[data = [row[0] for row in data["rows"]]]
    N -->|objects/object/array| P[if rows & columns -> convert rows to list of dicts]
    P --> Q{shape == "object"?}
    Q -->|yes| R{data contains "primary_keys"?}
    R -->|no| S[data = {"ok": False, "error": "_shape=object is only available on tables"}]
    R -->|yes| T{primary_keys non-empty?}
    T -->|no| U[data = {"ok": False, "error": "_shape=object not available for tables with no primary keys"}]
    T -->|yes| V[for each row: pk_string = path_from_row_pks(row, pks, not pks); object_rows[pk_string] = row; data = object_rows]
    Q -->|no and shape == "array"| W[data = data["rows"]]
    N -->|arrays| X[leave data as dict]
    N -->|other| Y[status_code = 400; data = error object]
    X --> Z[determine _nl]
    Y --> Z
    Z --> AA{_nl set and shape == "array"?}
    AA -->|yes| AB[body = newline-joined json.dumps(item) for item in data; content_type=text/plain]
    AA -->|no| AC[body = json.dumps(data); content_type=application/json]
    AB --> AD[headers = {}; if next_url -> headers["link"] = '<next_url>; rel="next"']
    AC --> AD
    AD --> AE[return Response(body, status_code, headers, content_type)]

## Examples:
Example data shapes are shown as JSON snippets to illustrate how arguments change the output. These examples omit actual Response object construction for brevity; the function wraps the shown body text in a Response with appropriate headers and status.

1) Default arrays shape (no args):
    Input args: {}
    Input data:
        {
          "rows": [[1, "Alice"], [2, "Bob"]],
          "columns": ["id", "name"],
          "primary_keys": ["id"]
        }
    Output body (application/json):
        {"rows": [[1, "Alice"], [2, "Bob"]], "columns": ["id", "name"], "primary_keys": ["id"]}

2) arrayfirst:
    Input args: {"_shape": "arrayfirst"}
    Input data:
        {
          "rows": [[1, "Alice"], [2, "Bob"]],
          "columns": ["id","name"]
        }
    Output body (application/json):
        [1, 2]

3) objects / array (rows converted to objects):
    Input args: {"_shape": "array"}  (or "_shape": "objects")
    Input data:
        {
          "rows": [[1, "Alice"], [2, "Bob"]],
          "columns": ["id","name"]
        }
    Output body (application/json):
        [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

4) object (map by primary key):
    Input args: {"_shape": "object"}
    Input data:
        {
          "rows": [[1, "Alice"], [2, "Bob"]],
          "columns": ["id","name"],
          "primary_keys": ["id"]
        }
    Output body (application/json):
        {
          "1": {"id": 1, "name": "Alice"},
          "2": {"id": 2, "name": "Bob"}
        }
    Error cases:
        - If "primary_keys" missing -> {"ok": False, "error": "_shape=object is only available on tables"}
        - If "primary_keys" present but empty -> {"ok": False, "error": "_shape=object not available for tables with no primary keys"}

5) newline-delimited JSON for arrays:
    Input args: {"_shape": "array", "_nl": "1"}
    Input data:
        [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]  (data after rows->objects conversion)
    Output body (text/plain):
        {"id": 1, "name": "Alice"}
        {"id": 2, "name": "Bob"}

6) Invalid _shape:
    Input args: {"_shape": "invalid"}
    Output status: 400
    Output body:
        {"ok": False, "error": "Invalid _shape: invalid", "status": 400, "title": None}

