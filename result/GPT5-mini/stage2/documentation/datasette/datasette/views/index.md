# `index.py`

## `datasette.views.index.IndexView` · *class*

## Summary:
IndexView is an asynchronous HTTP view that builds and returns the site index: a list of visible databases (and each database's visible tables and views), either rendered as HTML or returned as JSON depending on the request format.

## Description:
IndexView is intended to be instantiated as part of a Datasette application's view layer (it subclasses BaseView). Typical callers are the ASGI request router or view factory inside the Datasette application which dispatches HTTP GET requests for the root/index route to IndexView.get.

Responsibilities:
- Verify that the requesting actor has the "view-instance" permission before listing any databases.
- Iterate over configured databases and determine per-database visibility using the Datasette application's visibility APIs.
- For each visible database, gather visible table and view metadata (columns, primary keys, counts where available, FTS table, hidden flags, relationships counts).
- Build a per-database summary structure used by the HTML template or by JSON output.
- Support returning either an HTML-rendered index page or a JSON representation depending on request.url_vars["format"].

Boundary:
- IndexView is strictly a read-only, presentation-layer view: it queries database metadata and permissions but does not modify state.
- It relies on the Datasette application object (available as self.ds via BaseView) and on database objects exposed in self.ds.databases to provide metadata and permission checks.

## State:
Class attributes
- name (str): "index" — the view name used by routing/registration.

Instance attributes (inherited / expected from BaseView)
- self.ds: the Datasette application context. This object must provide:
  - ensure_permissions(actor, permissions_list): async method to assert actor permissions
  - check_visibility(actor, permission, target): async method returning (visible: bool, private: bool)
  - databases: mapping[str->Database] of configured databases
  - urls.database(name) -> str: URL path for the named database
  - metadata() -> dict: site metadata used in template context
  - cors (bool): whether CORS headers should be added for JSON responses
  - permission_allowed(actor, permission, default=True) -> bool or awaitable: to check instance-level permission
- Database objects (values of self.ds.databases) are expected to implement async methods accessed by IndexView.get:
  - table_names() -> list[str]
  - hidden_table_names() -> list[str]
  - view_names() -> list[str]
  - table_columns(table) -> list[dict] or similar
  - primary_keys(table) -> list[str]
  - fts_table(table) -> str|None
  - table_counts(limit:int) -> dict[str->int|None] (may return None values)
  - get_all_foreign_keys() -> dict[table -> {"incoming": [...], "outgoing": [...]}]
  - is_mutable (bool), size (int), hash (str or None)

Important module-level constants used by this view (defined elsewhere):
- COUNT_DB_SIZE_LIMIT: threshold used to decide whether to attempt table_counts for a database
- TRUNCATE_AT: maximum number of tables/views to include in the truncated preview per database

Class invariants:
- self.ds must be set and provide the APIs listed above before get() is invoked.
- The view does not mutate self.ds or database objects.

## Lifecycle:
Creation:
- Instantiate via usual BaseView construction used by the application framework (no custom __init__ defined on IndexView).
- No __init__ parameters are required by IndexView itself; it relies on BaseView to supply any required context (notably self.ds).

Usage:
- The primary entrypoint is the asynchronous method get(request).
  - Precondition: request must be an object with at least:
    - url_vars: mapping that contains key "format" (value truthy for JSON output, falsey/empty for HTML).
    - args: mapping-like object with .get(key, default) used to read query parameters (e.g., "_sort").
    - actor: identity describing the requester (passed to permission checks).
  - Typical call sequence inside get():
    1. await self.ds.ensure_permissions(request.actor, ["view-instance"])
    2. For each (name, db) in self.ds.databases.items():
       a. await self.ds.check_visibility(request.actor, "view-database", name)
       b. If database is visible:
          - collect table_names, hidden_table_names and view_names
          - for each view_name: call ds.check_visibility(..., "view-table", (db_name, view_name))
          - decide whether to call db.table_counts(...) depending on db.is_mutable and db.size vs COUNT_DB_SIZE_LIMIT
          - for each table: ds.check_visibility(..., "view-table", (db_name, table))
              * collect table_columns, primary_keys, fts_table, and count from table_counts if available
          - optionally compute relationship counts by calling db.get_all_foreign_keys()
          - build per-database summary dict and append to top-level databases list
    3. If request.url_vars["format"] is truthy, return a JSON Response (application/json) containing a dict of database-name -> database-summary. May add CORS headers if self.ds.cors is true.
    4. Otherwise, call await self.render(["index.html"], request=request, context={...}) to return an HTML response. Context includes:
       - "databases": list of database summary dicts built above
       - "metadata": self.ds.metadata()
       - "datasette_version": datasette.version.__version__
       - "private": not await self.ds.permission_allowed(None, "view-instance", default=True)

Destruction:
- IndexView has no explicit cleanup requirements. It does not open nor hold persistent resources that require closing. Any resources belong to self.ds or Database objects and should be managed by them.

## Method Map:
flowchart LR
  A[get(request)] --> B[ensure_permissions(actor, ["view-instance"])]
  B --> C{for each database in self.ds.databases}
  C --> D[check_visibility(actor, "view-database", name)]
  D -->|visible| E[table_names(), hidden_table_names(), view_names()]
  E --> F[for each view: check_visibility(..., "view-table", (name, view_name))]
  E --> G[maybe table_counts = db.table_counts(...) if allowed]
  E --> H[for each table: check_visibility(..., "view-table", (name, table))]
  H --> I[table_columns(), primary_keys(), fts_table(), count lookup]
  G --> J[if sort by relationships or no counts -> db.get_all_foreign_keys()]
  I --> K[build per-table dicts]
  F & K --> L[compute visible_tables, hidden_tables, truncated list]
  L --> M[append database summary to databases list]
  M --> N{if request format -> JSON Response else render template}
  N --> O[return Response or await render(...)]

## Raises:
- KeyError: if request.url_vars does not contain the "format" key (the code accesses request.url_vars["format"] directly).
- Any exception raised by await self.ds.ensure_permissions(...) on unauthorized or invalid actor — the concrete exception type is provided by the Datasette permission system (propagated).
- Any exception raised by self.ds.check_visibility(...) or database metadata calls (table_names, view_names, table_columns, primary_keys, table_counts, get_all_foreign_keys, etc.) will propagate; these indicate problems interacting with the database layer or misconfigured database objects.
- If db.table_counts(...) returns a mapping that contains None values, IndexView discards the counts mapping (no exception, but note this code path resets table_counts to {}).
- No exceptions are explicitly raised by IndexView itself; it propagates exceptions from its dependencies.

## Example:
- Context: the application constructs IndexView and provides it with a self.ds that implements the required Datasette APIs. An ASGI router calls IndexView.get for a GET request.
- Typical (conceptual) flow:
  1. Request arrives with request.actor and request.url_vars["format"] = "" (empty) for HTML.
  2. IndexView.get verifies instance-level permission via self.ds.ensure_permissions.
  3. IndexView iterates configured databases, skipping any database that check_visibility marks as not visible to the actor.
  4. For visible databases, IndexView collects tables and views metadata, computes truncated lists and counts, and builds a list of database summary dictionaries.
  5. Since format is empty, IndexView calls await self.render(["index.html"], request=request, context={...}) and returns the rendered HTML response.
- For a JSON call, request.url_vars["format"] should be truthy; IndexView returns an application/json Response containing a mapping of database names to their summaries. If self.ds.cors is enabled, CORS headers are included.

### `datasette.views.index.IndexView.get` · *method*

## Summary:
Handle an incoming HTTP GET for the site index: gather per-database summary information (tables, views, counts, visibility, colors, paths) and return either a JSON representation or render the index HTML template, without mutating IndexView state.

## Description:
This asynchronous method is the GET handler for the index route of the application. In typical usage it is invoked by the view dispatch mechanism (BaseView or the ASGI routing layer) when a client requests the root/index page. The method performs permission checks for viewing the instance, enumerates each configured database and its tables/views, collects metadata for display, and finally returns one of:
- a JSON Response of the collected database summaries when the request supplies a truthy "format" url variable, or
- a rendered "index.html" template that receives the same data in its context.

Why separate this into its own method:
- It encapsulates the full pipeline for building the index page (permissions, per-database introspection, truncation/sorting rules, response selection) and thus keeps dispatching and rendering concerns separated.
- The code is IO-heavy and asynchronous (calls many async database and permission methods), so having it as a distinct async handler clarifies lifecycle and error-handling behavior.

Known callers / lifecycle:
- The framework's view dispatch code that resolves the IndexView for the index route will call this method as the handler for GET requests. It runs during request handling, after the request object has been constructed and before any template rendering or response is returned.

## Args:
    request (object): The incoming request object provided by the ASGI / view framework.
        Required fields and attributes used by this method:
        - url_vars (Mapping[str, Any]): must contain key "format"; treated truthy to request JSON output.
        - args (Mapping[str, str]): query parameters; used to check request.args.get("_sort") == "relationships".
        - actor (Any): the request actor/identity, passed to permission checks.

## Returns:
    datasette.utils.asgi.Response or awaitable returning the same:
    - If request.url_vars["format"] is truthy: returns a Response whose body is a JSON string encoding a mapping of database name -> database summary object (uses CustomJSONEncoder). Content-Type is "application/json; charset=utf-8". If the Datasette instance has CORS enabled (self.ds.cors truthy), CORS headers are added to the returned headers.
    - Otherwise: returns the result of awaiting self.render(["index.html"], request=request, context=...), which is the rendered HTML page (the framework's render returns an awaitable Response-like object).

    Edge-case returns:
    - If there are no visible databases, an empty list is provided to templates and an empty JSON mapping is returned for JSON format.
    - Table row counts may be omitted (None) when counts were not collected (see Constraints below), and code uses "count" or 0 in sorting and summing logic accordingly.

## Raises:
    - Propagates any exceptions raised by called async helpers:
        * Errors from self.ds.ensure_permissions(...) if the actor lacks required permissions (permission-denial behavior defined by the datasource layer).
        * Errors from self.ds.check_visibility(...) for database/table visibility checks.
        * Errors from database methods (db.table_names(), db.view_names(), db.table_counts(), db.table_columns(), db.primary_keys(), db.fts_table(), db.get_all_foreign_keys(), etc.) such as I/O or database back-end errors.
        * Errors from self.render or self.ds.metadata/permission_allowed if those helpers raise.
    - The method itself does not raise new, explicit exceptions; it surfaces errors from the underlying subsystems.

## State Changes:
Attributes READ:
    - self.ds: used extensively (ensure_permissions, check_visibility, permission_allowed, metadata, cors flag, urls.database, .databases mapping).
    - self.ds.databases: iterated to inspect configured database objects.
    - self.render: invoked when rendering HTML output.
    - self.ds.urls.database: used to build database path values.
    - self.ds.cors: read to decide whether to add CORS headers.
    - __version__ (module-level import): read to include version in template context.

Attributes WRITTEN:
    - None. The method does not mutate attributes on self.

## Constraints:
Preconditions:
    - request.url_vars must contain the key "format" (value checked for truthiness).
    - request.args must be a mapping supporting .get("_sort").
    - request.actor must be present (any object acceptable) since it is passed to permission checks.
    - self.ds must be a properly initialized datasource object exposing:
        * ensure_permissions(actor, permissions)
        * check_visibility(actor, scope, subject)
        * permission_allowed(subject, permission, default=True)
        * metadata()
        * urls.database(name)
        * cors flag
        * databases mapping whose values are database objects implementing the DB methods used below.
    - Database objects must implement the following async methods/attributes used by the handler:
        * table_names()
        * hidden_table_names()
        * view_names()
        * table_counts(limit:int)
        * table_columns(table_name)
        * primary_keys(table_name)
        * fts_table(table_name)
        * get_all_foreign_keys()
        * hash (attribute)
        * is_mutable (attribute)
        * size (attribute)

Postconditions / guarantees after the call:
    - The returned Response contains either JSON or rendered HTML.
    - No IndexView instance attributes are modified by this invocation.
    - The produced database summary objects supplied to the template/JSON will always include the keys:
        name, hash, color, path, tables_and_views_truncated, tables_and_views_more, tables_count, table_rows_sum, show_table_row_counts, hidden_table_rows_sum, hidden_tables_count, views_count, private.
    - When JSON is returned, the JSON body maps each database name to its summary object.

## Side Effects:
    - Calls multiple async methods that generally perform I/O (permission checks, metadata queries, and DB introspection). These may perform network or disk I/O depending on datasource/backends.
    - May add CORS headers into the headers dict via add_cors_headers(headers) when returning JSON and self.ds.cors is truthy (this mutates the local headers dict before passing it to Response).
    - Invokes json.dumps(..., cls=CustomJSONEncoder) which serializes the summary objects to a JSON string.
    - No persistent mutations on self or the database configuration are performed by this method.

## Implementation notes and important behavior details:
    - Table row counts are only requested when either the database is immutable or its size is below COUNT_DB_SIZE_LIMIT; otherwise table_counts stays empty and counts are omitted.
    - If any value in table_counts is None the method discards table_counts (sets it to empty {}) to avoid presenting partial counts.
    - Sorting of tables/views for the truncated display uses a tuple key:
        (num_relationships_for_sorting, count or 0, name) in descending order; if request.args["_sort"] == "relationships" or table_counts is empty, num_relationships_for_sorting is computed from foreign keys returned by db.get_all_foreign_keys().
    - The truncated list of tables and views has maximum length TRUNCATE_AT; if there is space left after tables are selected, views are appended up to that limit.
    - The display color for a database is taken from the first 6 characters of db.hash when available; otherwise an MD5 hex digest of the database name is used (first 6 chars).

