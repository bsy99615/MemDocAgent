# `database.py`

## `datasette.views.database.DatabaseView` · *class*

## Summary:
Represents the Datasette "database" view handler that gathers metadata, tables, views, and canned queries for a single database and returns the context needed to render the database landing page or to delegate to a SQL query view when an inline SQL parameter is provided.

## Description:
This class implements the logic used to produce the data and template context for the per-database page in a Datasette instance. It is intended to be instantiated as part of the web routing layer (typically by the framework or by a factory that constructs view objects with a Datasette application object). The handler method data(...) is asynchronous and designed to be invoked with an HTTP request-like object (see "Inputs" below).

Why this abstraction exists:
- Encapsulates the process of validating access to a database, collecting a database's structure (tables, views, foreign keys, counts, FTS info), and assembling data needed by templates.
- Keeps concerns separated from lower-level database objects (db) and from higher-level request routing: DatabaseView focuses on converting database and permission information into the standard (data, template_context, template_choice) triple used by Datasette page renderers.

Typical callers/factories:
- Web router that resolves a request URL to the "database" route and instantiates this view with the Datasette app object (usually inherited from DataView).
- Other view code that needs the database landing-page context may instantiate and call DatabaseView.data(request).

## Inputs (to data()):
- request: an object with at least the following attributes:
    - url_vars (mapping): contains "database" route variable (string; may be tilde-encoded).
    - args (mapping): query parameters (gettable via .get); used to check "sql" and "_show_hidden".
    - actor: the current actor/actor representation used for permission checks.
- default_labels (bool, optional): not used by DatabaseView beyond signature compatibility (defaults to False).
- _size (optional): passed through to QueryView when an inline SQL query is executed.

The method is async and must be awaited by callers.

## Outputs (return value of data()):
A 3-tuple (data_dict, template_context_dict, template_choice)
- data_dict (dict): the data used by templates; contains:
    - "database" (str): canonical database name (db.name)
    - "private" (bool): whether the database is flagged private for this actor
    - "path" (str): URL path to this database (via self.ds.urls.database(database))
    - "size" (int|None): db.size
    - "tables" (list[dict]): list of table summaries (see below)
    - "hidden_count" (int): number of hidden tables present in tables
    - "views" (list[dict]): list of view summaries ({ "name": str, "private": bool })
    - "queries" (list[dict]): canned (saved) queries visible to the actor; each dict is query metadata plus a "private" bool
    - "allow_execute_sql" (bool): whether the actor is allowed to execute arbitrary SQL on this database
- template_context_dict (dict): secondary context provided to the template; contains:
    - "database_actions" (async callable -> list): an async function which, when awaited, returns a list of extra action links produced by plugins
    - "show_hidden" (str|None): value of request.args.get("_show_hidden")
    - "editable" (bool): True (this view sets editable True)
    - "metadata" (dict): merged metadata for this database (after inherited metadata update)
    - "allow_download" (bool): Datasette setting "allow_download" AND database is not mutable AND not in-memory
    - "attached_databases" (list[str]): names of attached databases
- template_choice (tuple): (primary_template_name, fallback_template_name), here (f"database-{to_css_class(database)}.html", "database.html")

Details of each table dict in data_dict["tables"]:
- "name" (str): table name
- "columns" (list[dict]): result from db.table_columns(table)
- "primary_keys" (list[str]): result from db.primary_keys(table)
- "count" (int): row count (from table_counts)
- "hidden" (bool): whether the table is considered hidden
- "fts_table" (str|None|False): result from db.fts_table(table)
- "foreign_keys" (list[dict]): foreign keys for that table (from get_all_foreign_keys)
- "private" (bool): whether the table is private for this actor

Special behavior:
- If request.args contains a "sql" parameter, DatabaseView validates that SQL is a SELECT (validate_sql_select) and delegates to QueryView(self.ds).data(request, sql, _size=_size, metadata=metadata). In that case DatabaseView returns whatever QueryView.data returns.

## State:
Class attributes:
- name (str): "database" (class-level identifier used by routing / templating)

Instance attributes (inherited/expected):
- ds (Datasette): the Datasette application object; DatabaseView expects self.ds to provide:
    - get_database(route) -> db object (raises KeyError when missing)
    - check_visibility(actor, permissions=...) -> awaitable returning (visible: bool, private: bool)
    - metadata(scope) -> dict
    - update_with_inherited_metadata(metadata_dict) -> None (mutates metadata)
    - get_canned_queries(database, actor) -> dict-like mapping of saved queries
    - permission_allowed(actor, permission, database, default=True) -> awaitable bool
    - setting(key) -> configuration value
    - urls.database(database) -> path/url string
  The db object returned by get_database must provide:
    - name (str), size (int|None)
    - table_counts(limit) -> mapping table -> count
    - hidden_table_names() -> iterable[str]
    - get_all_foreign_keys() -> mapping table -> list[foreign_key_dict]
    - view_names() -> iterable[str]
    - table_columns(table) -> list[dict]
    - primary_keys(table) -> list[str]
    - fts_table(table) -> any (identifier or None)
    - is_mutable (bool)
    - is_memory (bool)
    - attached_databases() -> iterable[db_object_with_name_attr]

Class invariants:
- After successful data() call, returned data_dict["database"] equals db.name (canonical).
- self.ds must be a valid Datasette instance with the methods listed above; DatabaseView does not validate that at construction time.

## Lifecycle:
Creation:
- DatabaseView does not declare its own __init__; it inherits construction from DataView. Callers typically instantiate with the Datasette application object as DataView/DatabaseView's constructor argument (e.g., DatabaseView(datasette)). The crucial requirement is that the instance has a working self.ds attribute.

Usage (typical sequence):
1. Instantiate the view with a Datasette instance (DataView.__init__).
2. Route a web request to this view and call await view.data(request, default_labels=False, _size=None).
3. data() will:
   - Decode the "database" route variable (tilde_decode),
   - Resolve the database via self.ds.get_database(route=...),
   - Verify access with self.ds.check_visibility(...),
   - Merge database metadata,
   - If request.args["sql"] exists -> validate_sql_select(sql) and delegate to QueryView,
   - Otherwise collect tables, views, canned queries, run plugin hooks (database_actions), compute attached databases and boolean flags and return the (data, template_context, template_choice) triple.
4. The caller uses the returned triple to render a template or return a response.

Destruction / cleanup:
- DatabaseView holds no resources that require explicit cleanup. Any database connections are managed by the Datasette/db object. No context-manager or close() is required on DatabaseView itself.

## Method Map (call flow)
graph LR
    A[Start: data(request)] --> B[tilde_decode(request.url_vars['database'])]
    B --> C[self.ds.get_database(route)]
    C -->|KeyError| E[raise NotFound("Database not found...")]
    C --> F[self.ds.check_visibility(actor, permissions=('view-database', 'view-instance'))]
    F -->|not visible| G[raise Forbidden(...)]
    F --> H[load metadata & update inherited metadata]
    H --> I{request.args.get('sql') ?}
    I -->|yes| J[validate_sql_select(sql)]
    J --> K[return await QueryView(self.ds).data(...)]
    I -->|no| L[collect table_counts, hidden_table_names, foreign_keys]
    L --> M[iterate view_names -> check_visibility -> append views]
    L --> N[iterate table_counts -> check_visibility -> gather table_columns, primary_keys, fts_table -> append tables]
    M & N --> O[sort tables, build canned_queries (check_visibility per query)]
    O --> P[database_actions plugin hooks via pm.hook.database_actions -> await await_me_maybe]
    P --> Q[attached_databases = await db.attached_databases()]
    Q --> R[assemble data_dict, template_context_dict, template_choice]
    R --> S[Return triple to caller]

## Raises:
- NotFound: raised when self.ds.get_database(route=database_route) raises KeyError — this is translated to NotFound("Database not found: <route>").
- Forbidden: raised when self.ds.check_visibility returns visible=False for the ("view-database", database) permission check.
- InvalidSql (or another error from validate_sql_select): when request.args["sql"] is present but fails the SELECT-only validation. (validate_sql_select is imported and may raise InvalidSql.)
- Any exceptions raised by underlying datasette or db methods (examples: KeyError, sqlite errors) will propagate unless handled by surrounding code.

## Edge cases and constraints:
- The "sql" query parameter is treated specially: DatabaseView only accepts SELECT statements for inline SQL; otherwise it delegates to QueryView which may produce a different shape of return or raise.
- The "allow_download" flag in template_context is computed as (self.ds.setting("allow_download") and not db.is_mutable and not db.is_memory).
- Database and table visibility are always checked via self.ds.check_visibility per-item and for views/canned queries; items that are not visible are omitted from the returned lists.
- Table sorting: tables are sorted by a tuple (hidden flag, name) which places visible tables before hidden ones and then alphabetically by name.

## Example:
Assuming a Datasette instance (ds) and an ASGI-compatible request object (request) that has request.url_vars["database"] and request.actor set:

    # Instantiate (in practice inherited DataView handles this)
    view = DatabaseView(ds)

    # Typical call in an async handler
    data, template_ctx, template_choice = await view.data(request)

    # If an inline SQL param is present:
    # request.args.get("sql") -> SQL string
    # DatabaseView validates it is a SELECT and forwards to QueryView

Notes:
- DatabaseView expects to be part of the Datasette application framework and to rely on the ecosystem of utilities (tilde_decode, validate_sql_select, pm plugin hooks, await_me_maybe, to_css_class) and the Datasette/db API surface described above.

### `datasette.views.database.DatabaseView.data` · *method*

## Summary:
Returns the context, template context, and template choice required to render the database details page for a requested database (or delegates to SQL query rendering when an inline SQL query is provided). Does not modify the DatabaseView instance itself but may update Datasette-wide inherited metadata.

## Description:
This asynchronous method is invoked when an incoming HTTP request targets a database route (i.e., the request's URL includes a database identifier in url_vars["database"]). It is responsible for preparing everything required to render the "database" page: validating permissions, collecting table/view/query metadata and counts, and building a context suitable for a template renderer.

Callers and lifecycle:
- Called by the view-dispatch layer that maps a request to this DataView handler when a client requests a database page.
- If the request contains a "sql" query parameter, this method delegates to QueryView.data to render results for that SQL and immediately returns that result instead of the database page.
- This method executes as part of request handling pipeline (authorization → metadata preparation → template context assembly).

Why separate:
- The database page needs to perform many discrete, reusable operations (permission checks, metadata composition, collecting table/view/query lists and related attributes). Encapsulating this logic in its own async method keeps routing and template rendering separation-of-concerns and allows delegation to QueryView when necessary.

## Args:
    request (object): Request-like object with at least:
        - url_vars (dict): must contain key "database" (URL-encoded route name).
        - args (dict-like): query parameters (used for "sql" and "_show_hidden").
        - actor (object): actor used for permission checks.
      The method assumes request.args.get(...) works like dict.get.
    default_labels (bool, optional): Defaults to False. (Present for caller compatibility; not used in the current implementation.)
    _size (int|None, optional): Optional page/response size value forwarded to QueryView.data when an inline SQL query is present. Can be None.

## Returns:
    tuple: (context_dict, template_context_dict, template_choice)
    - context_dict (dict): Data used by the template renderer and by the response layer. Keys:
        - "database" (str): canonical database name (db.name).
        - "private" (bool): whether the database is considered private for the current actor.
        - "path" (str): URL path for the database (self.ds.urls.database(database)).
        - "size" (int): the database size value as provided by db.size.
        - "tables" (list[dict]): list of table summaries (see table item structure below).
        - "hidden_count" (int): number of tables in the returned "tables" list with hidden==True.
        - "views" (list[dict]): list of visible views, each dict has "name" (str) and "private" (bool).
        - "queries" (list[dict]): visible canned queries; each entry is a copy of the canned query dict with an added "private" (bool) key.
        - "allow_execute_sql" (bool): result of await self.ds.permission_allowed(request.actor, "execute-sql", database, default=True).
      Table item structure (each element of "tables"):
        - "name" (str): table name.
        - "columns" (list[dict]): column metadata from db.table_columns(table).
        - "primary_keys" (list[str]): primary key column names from db.primary_keys(table).
        - "count" (int): row count from table_counts.
        - "hidden" (bool): whether the table is in hidden_table_names.
        - "fts_table" (str|None): name of FTS table if any from db.fts_table(table).
        - "foreign_keys" (list[dict]): foreign key info for the table from all_foreign_keys[table].
        - "private" (bool): whether the table is private for the current actor.
    - template_context_dict (dict): Additional context passed through to template rendering layer with values:
        - "database_actions" (callable async -> list): an async callable (no-arg) that, when awaited, will gather extra database action links by executing plugin hooks (pm.hook.database_actions) and returning a flat list.
        - "show_hidden" (str|None|bool): the raw value of request.args.get("_show_hidden") (used by template to decide whether to reveal hidden tables).
        - "editable" (bool): currently hard-coded True (indicates whether metadata editing UI should be shown).
        - "metadata" (dict): database-level metadata looked up from self.ds.metadata("databases").
        - "allow_download" (bool): boolean computed as self.ds.setting("allow_download") and not db.is_mutable and not db.is_memory.
        - "attached_databases" (list[str]): names of attached databases (from db.attached_databases()).
    - template_choice (tuple): (primary_template_name, fallback_template_name)
        - primary_template_name (str): a template filename tailored to the database, of the form "database-<css-safe-database-name>.html".
        - fallback_template_name (str): "database.html"

    Edge cases:
    - When request.args contains "sql", this method does not return the described tuple but instead returns whatever QueryView.data returns (delegation). That return may have a different shape; callers of DatabaseView.data must handle QueryView.data's return format.

## Raises:
    - NotFound: If the database route decodes to a route that self.ds.get_database(route=...) does not know (KeyError caught and converted to NotFound). Exact message: "Database not found: <route>".
    - Forbidden: If the actor is not permitted to view the database (permission check returns visible==False). Exact message: "You do not have permission to view this database".
    - InvalidSql (or other exception raised by validate_sql_select): If request.args contains "sql" and the provided SQL fails validation. This is raised by validate_sql_select and will propagate out of this method.
    - Any exceptions raised by QueryView.data when delegating to it (if "sql" supplied) will propagate unchanged.
    - Other unchecked exceptions from async calls (db methods, self.ds methods, plugin hooks) may propagate to the caller.

## State Changes:
    Attributes READ:
        - self.ds: datasette instance is read for many operations (get_database, check_visibility, metadata, update_with_inherited_metadata, get_canned_queries, permission_allowed, setting, urls).
        - (transitively) db: the returned database object (db.*) is read for table_counts, hidden_table_names, get_all_foreign_keys, view_names, table_columns, primary_keys, fts_table, attached_databases, size, is_mutable, is_memory.
    Attributes WRITTEN:
        - None of the explicit self.<attr> attributes are reassigned by this method.
        - Side-effect: self.ds.update_with_inherited_metadata(metadata) mutates datasette-wide metadata state (it updates inherited metadata in the Datasette instance). This is a mutation of self.ds (not of self).

## Constraints:
    Preconditions:
        - request.url_vars must contain a "database" key whose value is a route-encoded database identifier.
        - self.ds must expose the methods used: get_database(route), check_visibility(actor, permissions), metadata(key), update_with_inherited_metadata(metadata), get_canned_queries(database, actor), permission_allowed(actor, permission, resource, default), setting(key), urls.database(name).
        - The db object returned by self.ds.get_database must expose the called async methods and attributes listed in "Attributes READ".
    Postconditions:
        - If the method returns the described tuple (non-SQL delegation path), the returned context_dict will only include tables, views, and queries that the current actor is permitted to view (permission filtering applied individually per item).
        - Tables in the returned "tables" list are sorted by hidden first (False before True?) and then by table name; specifically sorted by key (t["hidden"], t["name"]) so non-hidden tables come before hidden ones and then by name ascending.
        - The "hidden_count" value equals the number of entries in "tables" whose "hidden" value is truthy.
        - The template_choice tuple will contain a specialized primary template filename (database-<css-classified-name>.html) and a generic fallback "database.html".

## Side Effects:
    - Calls self.ds.update_with_inherited_metadata(metadata) which mutates datasette metadata state.
    - May call QueryView.data (when "sql" parameter is present) which can execute SQL and perform I/O within the data layer.
    - Executes permission checks via await self.ds.check_visibility and await self.ds.permission_allowed — these may consult auth backends and thus trigger database/IO operations or external lookups.
    - Calls plugin hooks via pm.hook.database_actions and uses await_me_maybe to handle coroutine or direct-return hooks; plugin hooks may perform arbitrary plugin-side actions.
    - No file-system writes or direct HTTP responses are performed by this method itself; it returns data for the response layer to render.

## `datasette.views.database.DatabaseDownload` · *class*

## Summary:
Represents the view that handles downloading a physical SQLite database file for a named database route. It enforces permission checks and server configuration before returning a streamed file response or a 304 Not Modified response when ETag matches.

## Description:
DatabaseDownload is an asynchronous request handler (a DataView subclass) responsible for serving the underlying SQLite database file for a database identified by the route parameter "database". Typical callers:
- The web routing layer of the Datasette application: it instantiates or reuses this DataView and calls its async get(request) method when a "download database" URL is requested.
- Tests or administrative scripts exercising the download endpoint may call get(request) directly with a mock request.

Motivation and responsibilities:
- Centralize download-specific permission checks and feature-flag logic (allow_download setting).
- Validate that the target is a physical, non-memory, non-mutable database with an on-disk path.
- Add CORS headers when instance-level CORS is enabled.
- Provide HTTP conditional GET support using the database's stored hash as an ETag.
- Return an AsgiFileDownload object that will stream the file to the client; note that AsgiFileDownload will use and may modify the provided response headers mapping during streaming, so callers/frameworks should expect that headers may be updated by the streaming layer.

Responsibility boundaries:
- Does not implement low-level permission logic (delegates to self.ds.ensure_permissions).
- Does not perform path resolution beyond asking self.ds.get_database(route=...).
- Does not transform database file contents itself — it creates and returns the AsgiFileDownload streaming wrapper. However, the AsgiFileDownload streaming layer may read or update headers (for example adding content length or other streaming-related headers) when the response is actually sent.

## State:
Attributes used by this class (inherited or defined):
- name (class attribute) : str
  - Value: "database_download"
  - Purpose: view name used by the routing/dispatch system.
- self.ds : Datasette
  - Type: Datasette (framework instance provided by DataView)
  - Invariant: available and correctly configured when get() is called.
  - Used for: permission checks, retrieving database objects, configuration flags (setting, cors).
- request (method parameter) : Request-like object (not stored on the instance)
  - Expected shape (required fields used by this view):
    - request.url_vars : dict-like with key "database" -> str (route-encoded database name)
    - request.actor : actor/principal object (passed to permissions check)
    - request.headers : mapping of request headers; used to read "if-none-match"

Relevant database object (db) shape (returned by self.ds.get_database):
- db.is_memory : bool
  - True if the database is in-memory (no on-disk file).
  - Invariant: if True, db.path is expected to be falsy or not applicable. This view rejects downloads for memory DBs.
- db.is_mutable : bool
  - True if the database is writable/mutable (e.g., a live DB) — downloads are forbidden in this case.
- db.path : str or falsy
  - Filesystem path to the database file. The code requires this to be truthy; presence of the path is used as a prerequisite for returning a download response. The method does not itself validate file existence at this point — file I/O errors may still occur when streaming.
- db.hash : str or falsy
  - Stable hash representing the database content; used to compute an ETag header for conditional GET.

Class invariants:
- Before returning an AsgiFileDownload, the following must hold:
  - db exists for the requested route (no KeyError from get_database)
  - db.is_memory is False
  - self.ds.setting("allow_download") is truthy
  - db.is_mutable is False
  - db.path is a non-empty path-like string

## Lifecycle:
Creation:
- Instantiation is managed by the Datasette framework (DataView factory). No public __init__ parameters are required here beyond what DataView requires.
- The view is identified by its class attribute name "database_download" and wired to a route that provides a "database" url_var.

Usage (typical sequence when handling one request):
1. Request arrives routed to this view with request.url_vars["database"] containing a route-encoded database name.
2. get(request) is invoked (async).
3. The view decodes the route-encoded database name using tilde_decode.
4. It awaits self.ds.ensure_permissions(request.actor, [...]) to enforce:
   - "view-database-download" for that database
   - "view-database" for that database
   - "view-instance"
   Permission failures propagate (typically as Forbidden/DatasetteError depending on ensure_permissions).
5. It obtains the database object via self.ds.get_database(route=database). A KeyError leads to DatasetteError(status=404).
6. It verifies db.is_memory is False (rejects with 404 DatasetteError if True).
7. It verifies server setting allow_download is enabled and db.is_mutable is False. If either check fails, it raises Forbidden.
8. It verifies db.path is present (raises DatasetteError status=404 if missing).
9. Prepares response headers:
   - Adds CORS headers if self.ds.cors is truthy (via add_cors_headers).
   - If db.hash exists, sets Etag header to the quoted hash and checks request.headers.get("if-none-match"); if equal, returns Response("", status=304).
   - Sets "Transfer-Encoding": "chunked" header.
10. Returns an AsgiFileDownload configured with:
    - filepath = db.path
    - filename = os.path.basename(filepath)
    - content_type = "application/octet-stream"
    - headers = prepared headers
    Note: the AsgiFileDownload streaming layer may read and modify the supplied headers mapping when the response is sent; callers should not assume the headers remain unchanged.

Destruction / cleanup:
- No explicit cleanup is required by this class. The AsgiFileDownload wrapper and the ASGI framework are responsible for any file handle management and finalization. The view itself does not hold open file descriptors.

Sequencing constraints:
- Permission check must complete before attempting to access db metadata.
- ETag conditional response happens before creating the AsgiFileDownload response.

## Method Map:
Flowchart (Mermaid):

graph TD
    A[get(request)] --> B[tilde_decode(request.url_vars["database"])]
    B --> C[await ds.ensure_permissions(actor, permissions-list)]
    C --> D[ds.get_database(route=database)]
    D --> E{db exists?}
    E -- no --> F[raise DatasetteError("Invalid database", 404)]
    E -- yes --> G{db.is_memory?}
    G -- yes --> H[raise DatasetteError("Cannot download in-memory databases", 404)]
    G -- no --> I{allow_download && not db.is_mutable?}
    I -- no --> J[raise Forbidden("Database download is forbidden")]
    I -- yes --> K{db.path present?}
    K -- no --> L[raise DatasetteError("Cannot download database", 404)]
    K -- yes --> M[prepare headers (CORS, ETag, Transfer-Encoding)]
    M --> N{if ETag present and matches If-None-Match?}
    N -- yes --> O[return Response("", status=304)]
    N -- no --> P[return AsgiFileDownload(filepath, filename, content_type, headers)]

(Note: this diagram shows the decision points and normal/exception paths for the get method.)

## Raises:
The get(request) method raises or returns the following, based on runtime conditions:
- DatasetteError("Invalid database", status=404)
  - Trigger: self.ds.get_database(route=database) raises KeyError (no database for the requested route).
- DatasetteError("Cannot download in-memory databases", status=404)
  - Trigger: db.is_memory is True.
- Forbidden("Database download is forbidden")
  - Trigger: either self.ds.setting("allow_download") is falsy or db.is_mutable is True.
  - Notes: Forbidden may also be raised by self.ds.ensure_permissions if permission checks fail; permission failure semantics derive from the ensure_permissions implementation.
- DatasetteError("Cannot download database", status=404)
  - Trigger: db.path is falsy / no on-disk path is available.
- Response("", status=304)
  - Not an exception — an early-response value returned when the request's "If-None-Match" header equals the computed ETag based on db.hash.
- AsgiFileDownload(...)
  - Returned on success; the caller/framework must send this ASGI response to the client. The AsgiFileDownload object itself may perform further header adjustments or raise file-system related exceptions later when the framework attempts to open/read the file (e.g., FileNotFoundError) — callers should be prepared to handle such exceptions when sending the response.

Other propagated exceptions:
- Any exception raised by self.ds.ensure_permissions or self.ds.get_database that is not caught here will propagate (e.g., unexpected errors in underlying code).

## Example:
Typical handling scenario described in steps (framework-managed instantiation):
1. HTTP GET to /-/download/:database route with route param "database" set to "mydb" (route-encoded).
2. Router calls DatabaseDownload.get(request) with:
   - request.url_vars = {"database": "mydb"}
   - request.actor = currently authenticated actor/principal
   - request.headers = {"if-none-match": '"<hash>"'} (optional)
3. Inside get:
   - Permissions are checked for view-database-download/view-database/view-instance.
   - If checks pass and database is physical and allowed for download, headers are prepared:
     - ETag set to quoted db.hash if hash exists.
     - CORS headers added if ds.cors is enabled.
     - Transfer-Encoding header set to "chunked".
   - If ETag matches the client's If-None-Match header: return a 304 Response (no file sent).
   - Otherwise: return an AsgiFileDownload that streams the database file with filename set to basename(db.path) and content_type "application/octet-stream".
4. The ASGI server or framework receives the AsgiFileDownload return value and sends the streaming response; AsgiFileDownload may read and modify the provided headers mapping while preparing or streaming the response. DatabaseDownload itself has no further cleanup responsibilities.

Notes:
- This view intentionally sets a generic binary content_type (application/octet-stream); clients can rename the file based on the provided filename.
- The ETag uses the db.hash quoted as an HTTP ETag value. If your deployment proxies or caches responses, ensure proper handling of ETag and Range/Conditional semantics.

### `datasette.views.database.DatabaseDownload.get` · *method*

## Summary:
Serves a GET request to download a persisted SQLite database file: validates permissions, rejects in-memory or mutable databases or when downloads are disabled, handles conditional requests via ETag, and returns either a 304 response or an AsgiFileDownload that will deliver the database file.

## Description:
- Known callers and invocation context:
    - Invoked by the web routing layer when an HTTP GET is dispatched to the database-download endpoint (the view associated with DatabaseDownload). The request must include a url_vars mapping containing the "database" route variable.
    - Called during the HTTP request-handling lifecycle for a user-initiated database download. It runs as the request handler for the download route and is expected to return an ASGI-compatible response or a Response-like object.
- Why this is a separate method:
    - Encapsulates all download-specific checks (permission enforcement, database validity, download policy, conditional GET handling via ETag, and response construction) so routing logic stays simple and other view code can reuse or modify download behavior without duplicating security/validation logic.

## Args:
    request (object): Request object with at least the following attributes used by this method:
        - url_vars (mapping): must contain the "database" key whose value is the route fragment identifying the database (a string that will be passed through tilde_decode).
        - actor: the authenticated actor representation passed to self.ds.ensure_permissions.
        - headers (mapping): HTTP request headers; used to read "if-none-match" for conditional requests.
    (No default values.)

## Returns:
    AsgiFileDownload or Response
    - AsgiFileDownload: Returned when the database file is available for download and the request is not short-circuited by a conditional-match. The AsgiFileDownload is constructed with:
        - filepath: the database file system path (db.path)
        - filename: basename of the path
        - content_type: "application/octet-stream"
        - headers: dictionary populated with Etag (if available), Transfer-Encoding set to "chunked", and CORS headers if enabled
    - Response("", status=304): Returned when the database has a hash (db.hash) and the request sent an If-None-Match header that exactly equals the generated ETag (the ETag value is the db.hash wrapped in double quotes, e.g. '"<hash>"'). This implements conditional GET behavior.
    - Note: this method never streams content itself; it returns an object that the ASGI layer or response processing will use to perform file I/O.

## Raises:
    DatasetteError("Invalid database", status=404)
        - Triggered if self.ds.get_database(route=database) raises KeyError (the requested database route does not exist).
    DatasetteError("Cannot download in-memory databases", status=404)
        - Triggered when the resolved database object has is_memory truthy (in-memory databases are not downloadable).
    Forbidden("Database download is forbidden")
        - Triggered when either:
            - self.ds.setting("allow_download") is falsy (server configuration disallows downloads), OR
            - db.is_mutable is truthy (mutable databases are disallowed from being downloaded).
    DatasetteError("Cannot download database", status=404)
        - Triggered when the resolved database object has no filesystem path (db.path is falsy), i.e., there is nothing to download.

## State Changes:
- Attributes READ:
    - self.ds (reads methods/properties: ensure_permissions, get_database, setting, cors)
- Attributes WRITTEN:
    - None (the method does not modify any self.<attr> attributes)

## Constraints:
- Preconditions:
    - request.url_vars must include the "database" key.
    - self.ds must be set and implement:
        - ensure_permissions(actor, permissions_list) as an awaitable
        - get_database(route) which returns a database object or raises KeyError
        - setting(name) to return configuration flags (e.g., "allow_download")
        - cors attribute (truthy/falsey) indicating whether CORS headers should be added
    - The returned database object (db) must expose:
        - is_memory (bool), is_mutable (bool), path (str or falsy), and optionally hash (str or falsy)
- Postconditions:
    - On success, the returned response object will contain headers including:
        - "Transfer-Encoding": "chunked"
        - "Etag": '"<db.hash>"' if db.hash is truthy
        - plus any CORS headers added by add_cors_headers when self.ds.cors is truthy
    - No attributes on self are modified by this method.

## Side Effects:
- I/O / external behavior:
    - Calls self.ds.ensure_permissions which may trigger permission checks and plugin hooks and is awaited.
    - Calls self.ds.get_database which locates and returns database metadata; could raise KeyError.
    - Constructs and returns an AsgiFileDownload that, when processed by the ASGI response machinery, will perform filesystem reads to send the file to the client.
- Headers mutation:
    - Builds/modifies a local headers dict, adding Etag and Transfer-Encoding; add_cors_headers may add additional CORS-related headers to that dict.
- No persistent state is mutated on self or db by this method.

## `datasette.views.database.QueryView` · *class*

*No documentation generated.*

### `datasette.views.database.QueryView.data` · *method*

## Summary:
Executes a provided SQL string against a Datasette database and prepares the context needed to render a query page — supports SELECT rendering with plugin-driven cell formatting and an alternate write path that executes mutating SQL and returns JSON or redirect responses. This method does not modify the QueryView instance itself.

## Description:
This async handler centralizes the end-to-end processing of a query request:
- Resolves the database route from the request and obtains the Database object.
- Performs permission checks (different flow for canned queries vs ad-hoc SQL).
- Discovers and binds named SQL parameters, handling special underscore-prefixed parameters.
- For write flows (write=True): handles GET (show write form) and POST (execute write) differently, returning either a Response (JSON or redirect) or a template context for the write form.
- For read flows: executes the SQL (with truncation, optional page size / custom time limit), captures sqlite3.DatabaseError into an error payload, constructs display-ready rows via plugin hooks and markup logic, and produces template context + templates + status code.

Known callers and lifecycle stage:
- Called from HTTP route handlers when rendering a custom SQL page or canned query page. It runs during the request handling pipeline once routing, request parsing and actor identity are available.

Why this is a separate method:
- The method contains substantial branching (permissions, write vs read, plugin-driven rendering, blob URL generation, parameter derivation) that would clutter route handlers. Centralizing this logic makes it easier to test, reuse, and maintain.

## Args:
    request (object): Request-like object with attributes/methods used by the method:
        - url_vars (mapping): must include key "database" containing the tilde-encoded database route.
        - args (mapping-like): query parameters; supports .get(key) and iteration over keys.
        - method (str): HTTP method, e.g., "GET" or "POST".
        - headers (mapping-like): HTTP headers mapping; used to check Accept header.
        - post_body() coroutine: awaitable returning raw request body bytes (for POST).
        - path (str): request path used for redirect fallback.
        - actor (object): current actor used for permission checks.
    sql (str): SQL text to execute or validate. SELECT vs mutating semantics are controlled by the write flag and validation functions.
    editable (bool, optional): Whether the resulting template context should be marked editable. Defaults to True.
    canned_query (str | None, optional): Identifier for a canned query. When present:
        - A visibility check is performed (view-query / view-database / view-instance).
        - Parameter binding for both reads and writes uses MagicParameters.
    metadata (dict, required when used by caller): Metadata dict used for messages, redirects and hide_sql controls. The method accesses metadata.get(...) in multiple places — metadata must be a dict-like object (callers should pass {} if no metadata exists). If metadata is None, AttributeError will occur.
    _size (int | None, optional): If provided, passed as page_size to the execution layer (overrides default page size).
    named_parameters (iterable[str] | None, optional): If provided, used directly; otherwise derive_named_parameters(self.ds.get_database(database), sql) will be awaited to produce parameter names.
    write (bool, optional): If True, the method handles write flows (show write form on GET; execute write on POST). Defaults to False.

## Returns:
- write=True and request.method == "POST":
    - If request indicates JSON (Accept header equals "application/json", or _json in request.args or parsed body): returns a datasette.utils.asgi.Response JSON response containing {"ok": bool, "message": str, "redirect": str|None}.
    - Otherwise: returns a redirect Response produced via self.redirect(...) after adding a message into self.ds (side-effect).
- write=True and request.method != "POST":
    - tuple(page_data, extra_template_coroutine, templates)
        - page_data (dict): minimal context for the write form:
            - database (str), rows ([]), truncated (False), columns ([]), query ({"sql": sql, "params": params}), private (bool)
        - extra_template_coroutine (async function): returns dict used by template rendering (includes request, named_parameter_values, canned_write flag, etc.)
        - templates (list[str]): template name candidates (more specific first)
- write=False (read flow):
    - tuple(page_data, extra_template_coroutine, templates, status_code)
        - page_data (dict):
            - ok (bool): False if a sqlite3.DatabaseError occurred, otherwise True
            - database (str)
            - query_name (canned_query or None)
            - rows (list): results.rows if successful else []
            - truncated (bool): results.truncated if successful else False
            - columns (list[str])
            - query ({"sql": sql, "params": params})
            - error (str|None): stringified sqlite3.DatabaseError if occurred
            - private (bool)
            - allow_execute_sql (bool)
        - extra_template_coroutine (async function): returns full render-time context including display_rows; applies plugin rendering and formatting rules
        - templates (list[str])
        - status_code (int): 200 on success, 400 when sqlite3.DatabaseError occurred

Edge-case returns:
- The method does not return page-data tuples when a write POST is handled; it returns Response objects instead.
- If the SELECT execution fails with sqlite3.DatabaseError, the error is captured and converted into the returned page_data and a 400 status code (not re-raised).

## Raises:
    NotFound: If the database route from request.url_vars["database"] does not correspond to a known database (self.ds.get_database raises KeyError).
    Forbidden: Raised in these code paths:
        - When canned_query is provided and check_visibility returns visible == False.
        - When write=True and request.method == "POST" but db.is_mutable is False.
    Other exceptions:
        - If the actor lacks permissions, self.ds.ensure_permissions(...) is awaited — any exception it raises will propagate (in typical Datasette implementations this will be a permission/Forbidden-style exception).
        - Errors raised during write execution are caught and turned into messages/JSON responses; SELECT sqlite3.DatabaseError is caught and converted into the returned error payload and status code rather than being re-raised.

## State Changes:
Attributes READ:
    - self.ds (Datasette instance): used heavily for:
        - get_database(route), execute(database,...), databases[database].execute_write(...), permission checks (ensure_permissions, permission_allowed), settings and URLs, adding messages, and INFO/ERROR message constants.
    - request properties: url_vars, args, headers, method, actor, path, post_body coroutine.
    - pm (plugin manager): pm.hook.render_cell is iterated to allow plugins to override cell rendering.
    - sqlite3 (module alias imported): used to detect DatabaseError class.
Attributes WRITTEN:
    - None of the QueryView instance attributes are mutated.
    - External side-effect mutations:
        - Database mutations via self.ds.databases[database].execute_write(...) when handling write POST.
        - self.ds.add_message(request, message, message_type) adds a message to the Datasette instance.

## Constraints:
Preconditions:
    - request.url_vars must contain "database" (tilde-encoded route). tilde_decode is used to normalize it.
    - metadata must be a dict-like object (not None) if the caller expects metadata-driven behavior (the method calls metadata.get(...) unguarded).
    - When named_parameters is omitted, the database must be retrievable so derive_named_parameters(self.ds.get_database(database), sql) can run.
    - If write=True and request.method == "POST", request.post_body() must be awaitable and return the raw request body bytes.

Postconditions:
    - For read flows: returned page_data describes the result set (rows, columns, truncated) or contains an error string if execution failed; extra_template coroutine produces display_rows ready for rendering.
    - For write POST success: the database will be mutated, a message added to Datasette, and the caller receives a Response (JSON or redirect).
    - For write POST failure: the exception message is returned to the caller in JSON or added as a message before redirect.

## Side Effects:
    - Database write operations when handling POST writes (execute_write).
    - Messages added to self.ds via self.ds.add_message(request, message, message_type).
    - Returns of Response objects (JSON or redirect) that short-circuit template rendering.
    - Invokes plugin hooks via pm.hook.render_cell for each cell — plugin hook results may be awaitables and are handled via await_me_maybe.
    - Generates blob download URLs using path_with_format and SHA256 of blob bytes; no blob bytes are written/read here but URLs referencing blob endpoints are created.

## Implementation details important for reimplementation:
    - Parameter parsing:
        - params starts from request.args; "sql" and "_shape" keys are removed.
        - When parsing POST body for write:
            * body is decoded as UTF-8 and stripped.
            * If it begins with "{" and ends with "}", parsed as JSON and all values coerced to str.
            * Otherwise parsed via parse_qsl(..., keep_blank_values=True) into a dict.
        - JSON response mode is detected if Accept header equals "application/json" or request.args/_json flag present or parsed params contain "_json".
    - Named parameters:
        - derive_named_parameters(self.ds.get_database(database), sql) is called if named_parameters not provided.
        - named_parameter_values includes only named parameters that do not start with "_" and maps them to params.get(name) or "".
        - Any named parameter not present in params and not starting with "_" is added to params with an empty string value.
    - Execution options:
        - params["_timelimit"] if present sets extra_args["custom_time_limit"] = int(params["_timelimit"]).
        - _size, if provided, sets extra_args["page_size"] = _size.
    - Templates:
        - templates list ordered: "query-{db-css}-{canned-css}.html" (if canned), then "query-{db-css}.html", then "query.html".
    - Read execution:
        - results = await self.ds.execute(database, sql, params_for_query, truncate=True, **extra_args)
        - On sqlite3.DatabaseError, results is set to None and query_error recorded; columns set to [].
    - Display rendering (extra_template):
        - Iterates results.rows and results.columns, attempts plugin-rendering per cell via pm.hook.render_cell; first non-None plugin result is used.
        - Fallback rendering rules:
            * empty ("", None) -> Markup("&nbsp;")
            * URL strings -> anchor with truncated URL text (truncate length controlled by self.ds.setting("truncate_cells_html"))
            * bytes -> blob-download anchor with SHA256 hash passed via extra_qs and human-readable size via format_bytes
            * other values -> str(value) with truncation and ellipsis if longer than truncate_cells
        - edit_sql_url is computed only if:
            * permission_allowed(request.actor, "execute-sql", database, default=True) is True
            * validate_sql_select(sql) does not raise InvalidSql
            * the SQL does not contain the substring ":_" (private params)
        - Show/hide logic for SQL text relies on metadata.get("hide_sql") and request params "_show_sql"/"_hide_sql"; a hidden input field may be injected into the returned show_hide_hidden markup.

## `datasette.views.database.MagicParameters` · *class*

## Summary:
A dictionary-like wrapper that provides "magic" dynamic parameter resolution: when a key follows the special _prefix_suffix form it can be resolved by registered plugin handlers; otherwise it behaves like a normal mapping.

## Description:
MagicParameters is used wherever Datasette needs a mapping of named parameters that can include dynamic, computed values supplied by plugins. It wraps an ordinary dict (the provided data) and augments lookups so that keys beginning with an underscore and containing a prefix and suffix (e.g. _prefix_suffix) may be resolved by plugin-provided callables registered via the register_magic_parameters hook.

Typical scenarios / callers
- Constructed by Datasette view code that prepares parameters for SQL rendering, template rendering, or other parameterized operations where plugin magic parameters are supported.
- Plugins register handlers via pm.hook.register_magic_parameters(datasette=...) which supply (name, callable) pairs. Each callable is expected to accept (suffix, request) and return the resolved value (or raise KeyError to indicate it cannot resolve the specific suffix).

Motivation and responsibility
- Encapsulates the lookup rules and plugin-hook interaction in one place so callers can treat the object as a mapping while supporting extendable, dynamic parameter resolution.
- Responsibility: apply plugin magic parameter handlers during key lookup without modifying the original data mapping.

## State:
- Underlying mapping (inherited state)
    - Stored via dict superclass initialization with the provided data mapping.
    - Contains any statically-provided parameter names and values.
- Attributes:
    - _request (any request-like object)
        - Type: request-like (e.g., Starlette/ASGI Request in Datasette contexts)
        - Purpose: passed to plugin magic callables so they may use request-specific information (headers, user, path, query, etc.)
        - Constraint: read-only after construction; plugins may read attributes but MagicParameters does not validate the request shape.
    - _magics (dict[str, Callable[[str, Any], Any]])
        - Type: mapping from prefix string -> callable
        - Callable signature expected: function(suffix: str, request) -> resolved_value
        - Populated from pm.hook.register_magic_parameters(datasette=datasette), flattened and converted into a dict
        - Invariant: keys are prefixes (strings without the leading underscore), values are callables. If plugin(s) supply conflicting prefix names, later entries override earlier ones when dict() is constructed.
- Class invariants:
    - The mapping view acts like a dict for ordinary keys.
    - For keys matching the magic pattern (see __getitem__), if a matching prefix exists in _magics, the corresponding callable is invoked on each access.
    - If the underlying dict is empty, __len__ reports 1 (see __len__ details) — this preserves truthiness in contexts that expect at least one parameter.

## Lifecycle:
- Creation:
    - Instantiate with MagicParameters(data, request, datasette)
        - data: a mapping (commonly dict) of initial parameter names to values.
        - request: the request-like object to be forwarded to magic handlers.
        - datasette: Datasette instance used to call pm.hook.register_magic_parameters(datasette=datasette).
    - During __init__, plugin hook pm.hook.register_magic_parameters(datasette=datasette) is invoked; its outputs are flattened and turned into the _magics dict.
- Usage:
    - Common operations: len(instance) and instance[key] lookups.
    - Typical sequence:
        1. Create instance with initial data.
        2. Read values using instance[key] where key is parameter name.
            - For keys not matching the magic pattern, standard dict lookup is used.
            - For magic-pattern keys, plugin handlers may be invoked to compute values on demand.
- Destruction:
    - No explicit cleanup required. There is no open-resource management, no context-manager support, and no close() method.

## Behavior (detailed):
- Magic key pattern:
    - A key is treated as potentially "magic" when:
        - It starts with an underscore character '_' and
        - The key contains at least two underscore characters in total (key.count('_') >= 2)
    - Example magic keys:
        - _now_utc  (prefix = 'now', suffix = 'utc')
        - _user_id  (prefix = 'user', suffix = 'id')
    - Parsing:
        - The code uses key[1:].split("_", 1) to split into (prefix, suffix) at the first underscore after the leading one.
- Resolution algorithm (__getitem__):
    1. If key matches the magic pattern:
        - Extract prefix and suffix from key by removing the leading underscore and splitting once at the next underscore.
        - If prefix exists in _magics:
            - Call the magic function: _magics[prefix](suffix, self._request)
            - If the magic callable returns a value, that value is returned to the caller.
            - If the magic callable raises KeyError, control falls back to reading the stored dictionary value using normal dict lookup (super().__getitem__(key)).
                - If the fallback lookup succeeds, that value is returned.
                - If fallback lookup raises KeyError, it propagates to the caller.
            - Any other exception raised by the magic callable propagates unchanged.
        - If prefix not found in _magics, fall back to standard dict lookup (super().__getitem__(key)).
    2. If key does not match the magic pattern:
        - Standard dict behavior (super().__getitem__(key)).
- Length behavior (__len__):
    - Returns the underlying dict length (super().__len__()).
    - If the underlying dict is empty (length 0), __len__ returns 1 instead of 0. This ensures truthy behavior in templates or other contexts that query truthiness/length.

## Method Map:
flowchart TD
    A[Instantiate MagicParameters] --> B[__init__ calls pm.hook.register_magic_parameters]
    B --> C[_magics dict populated]
    C --> D[Use mapping: len() or __getitem__]
    D -->|len| E[__len__: return super().__len__() or 1]
    D -->|lookup key| F[__getitem__]
    F --> G{key starts with '_' and has >=2 '_'?}
    G -->|no| H[return super().__getitem__(key)]
    G -->|yes| I[split into prefix,suffix]
    I --> J{prefix in _magics?}
    J -->|no| H
    J -->|yes| K[call handler = _magics[prefix](suffix, request)]
    K --> L{handler raises KeyError?}
    L -->|yes| H
    L -->|no| M[return handler result]
    K --> N{handler raises other exception}
    N -->|yes| O[exception propagates]

## Raises:
- __init__:
    - Propagates any exceptions raised by pm.hook.register_magic_parameters(datasette=...), including but not limited to TypeError or ValueError if plugins return data in an unexpected shape. These are not wrapped by MagicParameters.
- __getitem__:
    - KeyError:
        - If the key is not magic and is not present in the underlying mapping, super().__getitem__(key) will raise KeyError.
        - If the key is magic and a plugin handler raises KeyError (signaling "I cannot resolve this suffix") and the fallback lookup into the underlying mapping does not find the key, KeyError will propagate.
    - Any other exception raised by a plugin handler (e.g., RuntimeError, ValueError) will propagate unchanged.

## Example:
- Example usage with a manually-injected magic handler (note: in real usage plugin handlers are provided via pm.hook.register_magic_parameters):

1) Prepare static data and a fake request object:
    data = {'username': 'alice', '_greet_morning': 'fallback-greeting'}
    request = SimpleNamespace(path='/example', user='alice')  # any request-like object

2) Create an instance and inject a magic handler for the 'greet' prefix:
    mp = MagicParameters(data, request, datasette=None)
    # For demonstration only: inject a magic handler directly
    mp._magics['greet'] = lambda suffix, req: f"Good {suffix}, {getattr(req, 'user', 'guest')}"

3) Lookup keys:
    mp['username']                -> returns 'alice'          (normal dict lookup)
    mp['_greet_morning']          -> returns 'Good morning, alice'  (magic handler invoked)
    mp['_greet_evening']          -> returns 'Good evening, alice'  (magic handler invoked)
    mp['_greet_unknown']          -> returns 'fallback-greeting' if handler raises KeyError, or fallback if original dict had value
    mp['_missing_key']            -> raises KeyError if no magic handler and not present in data

Notes:
- In production, do not mutate _magics from outside; shown here only to demonstrate the callable contract and runtime behavior.
- Plugin-provided callables should raise KeyError when they cannot resolve a particular suffix so that the instance can fall back to static values in the underlying mapping.

### `datasette.views.database.MagicParameters.__init__` · *method*

## Summary:
Initializes the MagicParameters mapping by storing the provided base data, recording the request context, and collecting plugin-provided "magic" parameter resolvers into an internal lookup.

## Description:
- Known callers and lifecycle:
    - Constructed by Datasette view code when preparing a mapping of named parameters for SQL rendering, template rendering, or other parameterized operations where plugin magic parameters are supported. It is used at request time as part of request handling and template/render preparation.
    - Typical lifecycle: created once for a request or parameter-rendering operation, then used for key lookups and length checks while rendering or executing statements.

- Why this logic is a dedicated method:
    - Encapsulates object initialization and plugin registration in one place so callers receive a ready-to-use mapping-like object. Keeping plugin collection in __init__ centralizes side effects and makes the dynamic resolution behavior easy to reason about and test, rather than scattering hook calls across lookup code.

## Args:
    data (mapping or iterable): Initial mapping or sequence of (key, value) pairs used to populate the underlying mapping storage. Accepted shapes are those accepted by the superclass initializer (commonly a dict or dict-like mapping). No mutation or validation of values is performed here.
    request (object): A request-like object (e.g., an ASGI/Starlette request or a simple request context) that will be forwarded to magic parameter resolvers. The object is stored as-is; resolvers may inspect attributes expected on the request.
    datasette (object): The Datasette application instance passed to the plugin hook so plugins can register resolvers that may need access to application-wide state.

## Returns:
    None

## Raises:
    - Any exception raised by pm.hook.register_magic_parameters(datasette=datasette) is propagated directly (for example, NameError, TypeError, ValueError) if plugins or the hook implementation produce invalid output.
    - TypeError or ValueError (or similar) may also be raised by dict(...) if the hook returns items that are not valid (key,value) pairs. These are not caught and will propagate to the caller.

## State Changes:
- Attributes READ:
    - None of self's attributes are read during initialization.

- Attributes WRITTEN:
    - self (mapping contents): The superclass initializer is invoked with data (super().__init__(data)), which populates the mapping state inherited from DataView/dict with the supplied data.
    - self._request: Set to the provided request argument.
    - self._magics: Set to a dictionary mapping magic-prefix -> resolver callable. Built by flattening the iterable(s) returned by pm.hook.register_magic_parameters(datasette=datasette) and converting to dict.

## Constraints:
- Preconditions:
    - The provided data must be a shape acceptable to the superclass initializer (e.g., a mapping or an iterable of key/value pairs).
    - request can be any object; resolver callables will assume it provides whatever fields they require.
    - datasette must be a valid object that plugin hook implementations expect; passing None may cause some hooks to raise.

- Postconditions:
    - After return, self._request references the provided request object.
    - After return, self._magics is a plain dict whose keys are magic-prefix strings and values are callables expected to accept (suffix, request) and return the resolved value (or raise KeyError to signal "cannot resolve").
    - The mapping-like object is populated with the provided data so normal dict-style lookups operate on those entries in addition to the magic resolution behavior implemented elsewhere.

## Side Effects:
    - Calls pm.hook.register_magic_parameters(datasette=datasette) to collect plugin-provided registrations. This may execute plugin code at initialization time (side-effecting code in hooks can run).
    - No I/O (file, network) is performed directly by this method, but plugin hook code invoked may perform arbitrary operations (IO, logging, DB access) depending on plugin implementations.

### `datasette.views.database.MagicParameters.__len__` · *method*

## Summary:
Return the number of stored mapping entries, but always report at least 1 so the object appears non-empty even when the underlying dict has zero keys.

## Description:
This method implements the container length protocol for MagicParameters. It delegates to the parent dict.__len__ to obtain the actual number of stored keys, and if that value is zero it returns 1 instead.

Known callers and contexts:
- The built-in len(magic_parameters) call.
- Any runtime construct that queries container size or emptiness (for example evaluating truthiness in code that checks if container is empty).
- Template engines (e.g., Jinja2) that call len() or check emptiness to decide rendering logic — useful because MagicParameters supports dynamic "magic" keys via __getitem__ that may be accessed even when the underlying dict is empty.

Why this is its own method:
- The class needs a specific, consistent length semantics (minimum 1) that differs from a plain dict. Encapsulating this logic in __len__ keeps that behavior centralized and ensures all size/emptiness checks observe the intended semantics rather than duplicating the guard everywhere.

## Args:
None

## Returns:
int
- The integer length of the mapping if greater than zero (the result of the normal dict.__len__).
- If the underlying dict length is zero, returns 1.
- Always returns an integer >= 1.

## Raises:
None — the implementation only calls the superclass length method; under normal circumstances no exceptions are raised by this method itself.

## State Changes:
Attributes READ:
- None of the explicit attributes defined on MagicParameters (e.g., self._request, self._magics) are read by this method.
- Internally it reads the mapping state managed by the dict superclass (i.e., the stored keys/count), via super().__len__().

Attributes WRITTEN:
- None. This method does not modify self or any external state.

## Constraints:
Preconditions:
- self should be a valid mapping instance (MagicParameters is a dict subclass); the dict machinery must be intact so super().__len__() returns an integer.

Postconditions:
- No mutation of self.
- The return value is an integer >= 1.
- The method does not attempt to enumerate or count "magic" keys exposed via __getitem__; it only uses the stored dict length and forces a minimum of 1.

## Side Effects:
- None. There are no I/O operations, external calls, or mutations of objects outside self.

### `datasette.views.database.MagicParameters.__getitem__` · *method*

## Summary:
Resolve and return a parameter value for a requested key; if the key follows the plugin "magic" pattern it may invoke a registered magic resolver, otherwise it returns the stored dict value. The call does not mutate the MagicParameters instance.

## Description:
This dict-style item accessor centralizes lookup logic for named parameters during request handling. Typical callers are view/template/SQL rendering code that evaluate parameters via params[key] while handling a request. MagicParameters is created per-request (see MagicParameters.__init__), and __getitem__ is invoked whenever code performs a square-bracket lookup on that mapping.

This logic is separate because it encapsulates:
- Detection of the "magic" naming convention (leading underscore plus at least one other underscore),
- Lookup and invocation of plugin-provided resolvers (self._magics),
- The fallback semantics when a resolver raises KeyError,
- A specific implicit behavior when a magic prefix is not registered (returns None without consulting the underlying dict).

## Args:
    key (str): The parameter name to retrieve.
        - Must be a str or another object that implements startswith(...) and count(...); the method calls key.startswith("_") and key.count("_") before any dict lookup.
        - Magic naming convention: key must start with "_" and contain at least one additional "_" (i.e., key.count("_") >= 2). For such keys:
            * prefix = key[1:].split("_", 1)[0]  (may be an empty string for keys like "__foo")
            * suffix = key[1:].split("_", 1)[1]
        - Examples:
            * "user_id" → not a magic (no leading underscore) → falls back to dict.
            * "_id" → not a magic (only one underscore total) → falls back to dict.
            * "_user_id" → magic (prefix "user", suffix "id") → resolver checked.
            * "__foo" → magic with empty prefix ("") and suffix "foo" → resolver for "" may be invoked.

## Returns:
    Any:
        - Non-magic keys (do not match the leading-underscore pattern) return the underlying mapping value via super().__getitem__(key) (or raise KeyError if missing).
        - If key matches the magic pattern and prefix is present in self._magics, returns whatever the resolver callable returns (including None). No fallback occurs when a resolver returns None.
        - If key matches the magic pattern but prefix is not present in self._magics, the method returns None (implicit fall-through) and does NOT consult the underlying dict.
        - If a magic resolver raises KeyError, that KeyError is caught and the method falls back to return super().__getitem__(key) (which may raise KeyError).
        - Any non-KeyError exception raised by a resolver propagates to the caller.

## Raises:
    KeyError:
        - Raised by the fallback dict lookup (super().__getitem__(key)) when:
            1) A non-magic key is missing from the underlying mapping.
            2) A magic resolver raised KeyError (caught) and the underlying mapping lacks the key.
    AttributeError:
        - If key does not implement startswith/count (e.g., an int), the initial key.startswith(...) call will raise AttributeError before any dict lookup occurs.
    Any other exception:
        - Any non-KeyError exception raised by a magic resolver is not caught here and will propagate unchanged.

## State Changes:
    Attributes READ:
        - self._magics: checked to determine whether to invoke a resolver for the computed prefix.
        - self._request: passed as the second argument to the resolver callable.
        - underlying dict storage (via super().__getitem__) is read for non-magic keys or fallback after a resolver KeyError.
    Attributes WRITTEN:
        - None. This method does not modify self.

## Constraints:
    Preconditions:
        - MagicParameters.__init__ must have populated self._magics (mapping of prefix -> callable) and self._request.
        - key should be a str (or implement startswith and count) to avoid AttributeError.
    Postconditions:
        - The MagicParameters instance remains unchanged.
        - The caller receives either:
            * the resolver's return value (if invoked and did not raise KeyError),
            * the underlying dict value (if non-magic or if resolver raised KeyError and fallback succeeded),
            * None (if key looked like a magic but its prefix had no registered resolver),
            * or a KeyError/other exception if no value could be resolved or an exception propagated.

## Side Effects:
    - Invokes plugin-provided resolver callables self._magics[prefix](suffix, self._request) when a matching prefix exists. Those callables may perform arbitrary work (I/O, database access, mutate external state) and thus can produce side effects outside this object.
    - The method itself performs no I/O and does not mutate global state.

