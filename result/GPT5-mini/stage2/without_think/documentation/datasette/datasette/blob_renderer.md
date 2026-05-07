# `blob_renderer.py`

## `datasette.blob_renderer.render_blob` · *function*

## Summary:
Return an HTTP Response that serves a single BLOB column value from provided query rows, optionally validating a SHA-256 hash and producing a safe download filename.

## Description:
This async helper is used during HTTP request handling to serve raw binary (BLOB) content for a specific column from a query result. It performs argument validation, optional hash-based verification (to support time-limited links), filename construction, header setup to force download and prevent MIME sniffing, and returns a datasette.utils.asgi.Response containing the binary payload.

Typical callers / invocation context:
- Called by request handlers that implement "download blob" endpoints or column-rendering logic when a client requests the raw BLOB for a row.
- The caller supplies:
  - rows: query result rows (each row must be indexable by column name),
  - columns: the set/list of column names available in the rows,
  - request: an ASGI-style request wrapper exposing args (query parameters) and url_vars (path variables).
- The function is designed to be reused so all callers share consistent validation, filename composition, and response headers.

Why this is a separate function:
- Centralizes security and UX behavior for serving BLOBs (required query param checks, column validation, optional content-hash verification, filename sanitation using to_css_class, and Response creation). This avoids duplicating logic across multiple request handlers.

## Args:
    datasette (object):
        The Datasette application instance. Present for signature consistency; not used directly in this function.
    database (str | None):
        Database name or identifier. Present for signature consistency; not used directly here.
    rows (Sequence or iterable of row-like objects):
        Rows returned by a query. Each row must support item access by column name (row[<column_name>]). If no hash parameter is supplied the function will use rows[0], so callers must ensure rows is indexable and non-empty in that case. If a hash parameter is supplied, the function will iterate rows until it finds a row whose blob column's SHA-256 digest matches the provided hex digest.
        - Expected element type for the blob column: bytes (binary). If values are None or falsy, the response body becomes empty bytes (b"").
    columns (Sequence[str]):
        Sequence of valid column names. The requested blob column (from request.args[_BLOB_COLUMN]) must be present in this sequence.
    request (object):
        Request wrapper exposing at least:
        - args: mapping of query parameters (string -> string). Must contain the _BLOB_COLUMN key (module-level constant). May contain _BLOB_HASH for optional verification.
        - url_vars: mapping of path variables; if "pks" is present it will be included in the generated filename.
    table (str | None):
        Optional table name used when building the filename. If provided it is sanitized via to_css_class before inclusion.
    view_name (str | None):
        Name of the view that produced the rows (not used in this function).

Notes on module-level constants:
- This function expects module-level string constants:
  - _BLOB_COLUMN — the query-parameter key for selecting which column to serve.
  - _BLOB_HASH — the optional query-parameter key containing a SHA-256 hex digest to validate content.

## Returns:
    datasette.utils.asgi.Response
    - body: the selected blob bytes, or b"" if the stored value is falsy (None/empty).
    - status: 200 on success.
    - headers:
        - "X-Content-Type-Options": "nosniff"
        - "Content-Disposition": 'attachment; filename="{filename}"'
          where filename is composed of (in order, separated by hyphens): sanitized table (if present), the "pks" url_var (if present), sanitized column name, and (if a hash was provided) the first 6 characters of the hash; the filename ends with ".blob".
    - content_type: "application/binary"

All successful return flows:
- When a matching row is found (either first row when no hash is provided, or a row matching the provided hash), the Response with status 200 and the blob body is returned.

## Raises:
    datasette.utils.asgi.BadRequest
    - If the required query parameter for selecting the blob column is missing:
        - Condition: _BLOB_COLUMN not present in request.args
        - Message: "?{_BLOB_COLUMN}= is required"
    - If the requested blob column is not listed in columns:
        - Condition: blob_column not in columns
        - Message: "{blob_column} is not a valid column"
    - If _BLOB_HASH is provided but no row's blob value matches its SHA-256 hex digest:
        - Condition: _BLOB_HASH in request.args and for every row, hashlib.sha256(row[blob_column]).hexdigest() != provided_hash
        - Message: "Link has expired - the requested binary content has changed or could not be found."

    IndexError
    - Condition: request does not include _BLOB_HASH and rows is empty (the function attempts rows[0]).
    - Caller responsibility: provide at least one row when not using the hash lookup path.

    TypeError (propagated from hashlib.sha256 or from using non-bytes values)
    - Condition: a value passed to hashlib.sha256 is not a bytes-like object (e.g., None or str) during the hash-checking path.
    - Note: The function does not coerce types; callers must ensure blob values are bytes when using the hash parameter.

    KeyError or other lookup errors
    - Condition: row[blob_column] access fails because a row object does not support lookup by the column name or the column is missing for that row.
    - Note: columns is validated, but inconsistent row types can still raise lookup errors; callers should ensure rows are consistent with columns.

## Constraints:
Preconditions:
- request.args must be a mapping-like object.
- columns must enumerate the actual column names accessible on rows.
- If no _BLOB_HASH is provided, rows must be indexable and contain at least one element.
- If _BLOB_HASH is provided, blob values iterated must be bytes-like for hashing.
- Module-level constants _BLOB_COLUMN and _BLOB_HASH must be defined as strings.

Postconditions:
- On success, a Response is returned with status 200, headers to prevent MIME sniffing and to prompt file download, and a binary body equal to the selected blob or b"".
- No external state (files, DB, globals) is mutated.

## Side Effects:
- No file or network I/O occurs in this function.
- No persistent mutation of external state; the function only constructs and returns a Response object.

## Control Flow:
flowchart TD
    Start([Start])
    A{_BLOB_COLUMN in request.args?}
    A -- No --> BadReq1[BadRequest("?{_BLOB_COLUMN}= is required")]
    A -- Yes --> GetCol[blob_column = request.args[_BLOB_COLUMN]]
    B{blob_column in columns?}
    GetCol --> B
    B -- No --> BadReq2[BadRequest("{blob_column} is not a valid column")]
    B -- Yes --> HasHash{_BLOB_HASH in request.args?}
    HasHash -- Yes --> ForRows[Iterate rows:]
    ForRows --> CheckHash[Compute hashlib.sha256(row[blob_column]).hexdigest() == blob_hash?]
    CheckHash -- True --> SelectRow[Use this row; break]
    CheckHash -- False --> ForRows
    ForRows -- Exhausted --> BadReq3[BadRequest("Link has expired - the requested binary content has changed or could not be found.")]
    HasHash -- No --> NonEmpty{rows non-empty?}
    NonEmpty -- No --> IndexErr[IndexError (rows[0] on empty sequence)]
    NonEmpty -- Yes --> SelectFirst[row = rows[0]]
    SelectRow --> Prepare[value = row[blob_column]]
    SelectFirst --> Prepare
    Prepare --> BuildFilename[Compose filename bits (to_css_class(table), url_vars["pks"], to_css_class(blob_column), blob_hash[:6])]
    BuildFilename --> MakeHeaders[Set X-Content-Type-Options and Content-Disposition]
    MakeHeaders --> ReturnResp[Return Response(body=value or b"", status=200, headers=..., content_type="application/binary")]
    BadReq1 --> End([End])
    BadReq2 --> End
    BadReq3 --> End
    IndexErr --> End
    ReturnResp --> End

## Examples (realistic usage and error handling):
- Serving the first-row blob (no hash protection):
  1. A request arrives with query ?{_BLOB_COLUMN}=photo.
  2. Handler queries the database and obtains columns=['id','photo'] and rows=[row0, ...].
  3. Handler calls render_blob(datasette, "db", rows, columns, request, "photos", view_name).
  4. If rows is non-empty and row0['photo'] is bytes, the client receives a 200 Response with the photo bytes and a filename like "photos-1-photo.blob".
  5. If rows is empty, the call raises IndexError — the handler should validate rows before calling or map this to an HTTP 400/404 as appropriate.

- Serving a hash-protected blob:
  1. A request arrives with query ?{_BLOB_COLUMN}=photo&{_BLOB_HASH}=<hex>.
  2. The function iterates rows and computes hashlib.sha256(value).hexdigest() for each row's photo.
  3. If a match is found, that row's photo bytes are returned (200).
  4. If no match is found, the function raises BadRequest with message "Link has expired - the requested binary content has changed or could not be found."
  5. If any row's photo value is not bytes-like, hashlib.sha256 will raise TypeError which propagates; callers should ensure stored blob values are bytes for hash-protected links.

Caller guidance:
- Validate rows presence when not using hash verification, or catch IndexError and return an appropriate HTTP response (e.g., 400/404).
- Ensure blob values are stored as bytes when using hash-protected download links to avoid TypeError during hashing.
- Treat BadRequest exceptions from this function as client errors and surface the message to the user or translate to a 400 response.

## `datasette.blob_renderer.register_output_renderer` · *function*

## Summary:
Returns a renderer registration dictionary for serving raw BLOB output, providing the renderer extension, the callable that will produce the Response, and a can_render predicate (which is always false).

## Description:
This function produces the canonical metadata object used by Datasette's renderer registration system to expose a "blob" output format. Rather than performing rendering itself, it returns a dictionary describing:
- the extension string clients may request (extension = "blob"),
- the callable to invoke to perform rendering (render = render_blob),
- a can_render function used by the renderer selection process (can_render = lambda: False).

Known callers / invocation context:
- Intended to be discovered and invoked by Datasette's plugin / hook system when collecting output renderers for the application (i.e., as a hook implementation that returns renderer metadata). No direct internal callers were identified in the provided code snapshot; the returned dictionary is consumed by the renderer registry or routing logic elsewhere in the application when a ".blob" output is requested.
- At runtime the renderer registry will call the returned render callable (render_blob) to produce a datasette.utils.asgi.Response for a specific request.

Why this logic is a separate function:
- Encapsulates the renderer metadata in one place so plugin registration is explicit and consistent.
- Keeps the mapping between the "blob" extension and the actual implementation (render_blob) declarative and easy to register/unregister by plugin discovery code.
- Separates the small registration contract from the heavier rendering implementation (render_blob) so the latter can be tested and maintained independently.

## Args:
- This function takes no arguments.

## Returns:
- dict with the following keys:
    - "extension" (str): the extension string for this renderer. Always "blob".
    - "render" (callable): the rendering callable to invoke to produce the response. This is the render_blob function defined in the same module. Expected signature (as required by render_blob):
        (datasette, database, rows, columns, request, table=None, view_name=None)
      The callable must accept these parameters and return a datasette.utils.asgi.Response.
    - "can_render" (callable): a zero-argument callable returning bool. This function is always a lambda that returns False; this signals that the renderer should not be automatically selected by generic renderer-selection logic and must be explicitly requested (for example by using the ".blob" extension).

All possible return values:
- The function always returns the same static dictionary. There are no alternate return branches.

## Raises:
- This function does not raise exceptions. It only constructs and returns a dictionary.

## Constraints:
Preconditions:
- The module-level render_blob symbol must be defined and be a callable with the expected signature (see Returns).
- The runtime/plugin loader that consumes this dictionary expects keys "extension", "render", and "can_render" with the documented types.

Postconditions:
- After calling this function the caller receives a stable renderer-metadata dict mapping "blob" to the render_blob implementation and a can_render predicate that always returns False.
- No state is mutated by this function.

## Side Effects:
- None. The function performs no I/O and does not modify global state — it simply returns a short dictionary.

## Control Flow:
flowchart TD
    Start([Start])
    CreateDict[Create dict:
      extension: "blob",
      render: render_blob,
      can_render: lambda: False]
    ReturnDict[[Return dict]]
    Start --> CreateDict --> ReturnDict --> End([End])

## Examples (usage and intent):
- Typical plugin registration flow (descriptive):
  1. The Datasette plugin/hook discovery system loads plugin modules and calls functions that return renderer registration dictionaries.
  2. Calling this function yields a dictionary associating the "blob" extension with the render_blob callable and a can_render predicate that always returns False.
  3. When an incoming HTTP request explicitly requests the "blob" renderer (for example via a ".blob" path/extension or via explicit renderer selection), the renderer registry will call the "render" callable from this dictionary to produce the binary Response.
  4. Because can_render always returns False, generic renderer-selection logic will not pick this renderer automatically; it must be selected explicitly by the request path or by the registry when the extension is requested.

- Manual retrieval (descriptive):
  - A component that needs to inspect available renderers can call register_output_renderer() to obtain this renderer's metadata and then invoke the "render" function with the appropriate arguments (matching render_blob's contract) to obtain a datasette.utils.asgi.Response containing the blob bytes.

Notes:
- The returned can_render predicate being constantly False is deliberate: it prevents implicit selection and requires explicit selection of the "blob" renderer (for example when the request path ends with ".blob" or when the application chooses it explicitly).

