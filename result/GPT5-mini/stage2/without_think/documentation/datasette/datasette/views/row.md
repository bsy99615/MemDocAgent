# `row.py`

## `datasette.views.row.RowView` · *class*

## Summary:
Represents the view that retrieves and prepares a single database row for rendering. It enforces visibility permissions, fetches the row by primary-key components, and provides both raw data and a lazily-evaluated template data coroutine for rendering row detail pages.

## Description:
RowView is an asynchronous DataView subclass used by the request handling pipeline to produce the payload required to render a single-record detail page for a table. It is instantiated and managed by the web framework / view factory that wires DataView subclasses into route handlers. The primary responsibilities of RowView are:
- Resolve the requested database and table from route variables.
- Enforce access control (visibility) for the requesting actor.
- Parse URL-safe primary key components and build a parameterized SQL query that selects the requested row(s).
- Execute the query, erroring with NotFound if no record is returned.
- Return an immediate data dict (raw rows, columns, primary key info, units metadata), a coroutine (template_data) which when awaited returns display-ready columns/rows and foreign-key information, and an ordered tuple of template names to try when rendering.

Typical callers:
- The Datasette view-renderer or route handler that maps a URL like /{database}/{table}/{pks} to RowView.data(request).
- Tests and utilities that need a consistent representation of a single-row response.

Separation of concerns:
- RowView keeps low-level SQL construction to _sql_params_pks and display transformation to display_columns_and_rows; RowView orchestrates these helpers and coordinates permission checks and result packaging.

## State:
Public class attributes and instance state required or used by RowView:

- name (str)
  - Value: "row"
  - Purpose: identifies the view type; used by routing or templating logic.
  - Invariant: constant for the class.

- ds (Datasette-like object) — required (provided by DataView base)
  - Type: object implementing Datasette API surfaced in this file (duck-typed).
  - Required methods/attributes (used by RowView):
    - get_database(route: str) -> Database-like object
      - Raises KeyError if route not found (RowView catches and converts to NotFound).
    - check_visibility(actor, permissions: list) -> coroutine that resolves to (visible: bool, private: bool)
    - metadata(namespace: str) -> dict-like (used to find per-database/table metadata)
    - table_metadata(database: str, table: str) -> dict (used to read "units")
    - databases (mapping): mapping of database_name -> Database-like object (used by foreign_key_tables)
    - urls.table(database: str, table: str) -> str (returns URL path for a table)
  - Invariant: ds must be initialized and consistent across calls.

- Methods and their contracts:
  - async def data(request, default_labels=False) -> (dict, coroutine, tuple[str, ...])
    - Uses ds extensively; see "Lifecycle" and "Raises".

  - async def foreign_key_tables(database: str, table: str, pk_values: Sequence[str]) -> list[dict]
    - No stored state; purely computed from ds and its Database objects.

Class invariants (conditions that should hold while using RowView):
- self.ds must be a valid Datasette instance with the expected API.
- Calls to self.ds.get_database(route=...) should return objects with .name and .execute method as described below.
- For the same request, repeated invocations may re-query the database; RowView does not cache results internally.

## Lifecycle:
Creation:
- RowView instances are constructed by the application framework (DataView factory). The framework must supply a Datasette-like object on the instance (commonly via the DataView base class __init__). There is no custom RowView __init__ in the source; therefore instantiation requirements are:
  - The instance must have attribute .ds set to a Datasette-like object prior to calling data() or foreign_key_tables().
  - The class attribute name = "row" is present by default.

Usage (typical sequence):
1. Framework creates RowView and ensures self.ds is set.
2. Request arrives and the framework calls await row_view.data(request).
   - request must be an object with:
     - url_vars: mapping containing "database" (route-encoded string), "table" (route-encoded string), and "pks" (route-encoded PK components path).
     - args: mapping-like (e.g., querystring parameters) used to inspect "_extras" for optional inclusion of foreign_key_tables in the immediate data dict.
     - actor: identity passed to ds.check_visibility for permission evaluation.
3. RowView.data performs:
   - decode route components (tilde_decode)
   - resolve database via ds.get_database(route=...)
   - call ds.check_visibility(...) to ensure the actor can view the table
   - parse PKs via urlsafe_components(request.url_vars["pks"])
   - build SQL + params + pks via _sql_params_pks(db, table, pk_values)
   - execute the query via db.execute(sql, params, truncate=True)
   - validate results; raise NotFound if no rows
   - construct data dict and a coroutine template_data that when awaited:
     - calls display_columns_and_rows(...) to produce display_columns and display_rows
     - disables "sortable" on display_columns
     - calls self.foreign_key_tables(database, table, pk_values)
     - returns metadata and custom_table_templates and private flag
4. Optionally, if request.args["_extras"] contains "foreign_key_tables", RowView.data will eagerly add foreign_key_tables to the returned immediate data dict (awaiting self.foreign_key_tables).
5. The framework uses the returned (data, template_data, templates) to render a template:
   - It may await template_data() to get additional render-time information.

Destruction:
- RowView holds no resources requiring explicit cleanup. No context manager or close() method is required or present.

Concurrency notes:
- data() and foreign_key_tables() are async; callers should await them.
- template_data is a coroutine factory (an async function) returned to the caller and must be awaited to produce additional template context. Multiple awaits of template_data will re-run its logic (it is not memoized).

## Method Map:
graph TD
    A[Request arrives] --> B[data(request)]
    B --> C[tilde_decode database & table]
    C --> D[ds.get_database(route)]
    D --> E[ds.check_visibility(actor, permissions)]
    E --> F[urlsafe_components(pks)]
    F --> G[_sql_params_pks(db,table,pk_values)]
    G --> H[db.execute(sql, params, truncate=True)]
    H --> I[rows/results found? -> NotFound if none]
    I --> J[construct immediate data dict]
    J --> K[return (data, template_data, templates)]
    K --> L[caller optionally await template_data()]
    L --> M[display_columns_and_rows(...)]
    M --> N[self.foreign_key_tables(database,table,pk_values)]
    N --> O[template-ready dict returned to renderer]

(Above flow shows the dominant control flow and call relationships between RowView methods and helpers.)

## Raises:
RowView.data:
- NotFound:
  - If ds.get_database(route=...) raises KeyError for the route (database does not exist).
  - If the SQL query produced by _sql_params_pks returns no rows (no matching record for provided PKs).
- Forbidden:
  - If ds.check_visibility(...) returns visible == False.
- QueryInterrupted:
  - May propagate if db.execute(sql, params, truncate=True) raises QueryInterrupted (not caught inside data()). Other DB exceptions from execute will also propagate.
- Any exceptions raised by helper functions (tilde_decode, urlsafe_components, _sql_params_pks, display_columns_and_rows) will propagate unless explicitly handled by callers.

RowView.foreign_key_tables:
- Returns [] instead of raising if:
  - len(pk_values) != 1 (method only supports single-column PKs).
  - No incoming foreign keys for the table.
  - A QueryInterrupted occurs while executing the count query.
- May raise KeyError if:
  - database is not found in self.ds.databases
  - the database.get_all_foreign_keys mapping doesn't contain the target table key.
- Other exceptions from ds.urls.table or db.execute (other than QueryInterrupted) will propagate.

## Example:
Scenario: the framework wishes to render the detail page for a row at route variables {database: "db", table: "notes", pks: "<encoded-pk>"}.

- Preconditions:
  - A RowView instance exists and has .ds pointing to an initialized Datasette-like object.
  - request is provided containing url_vars, args, actor.

- Typical invocation pattern (conceptual; not code pasted):
  1. result = await row_view.data(request)
     - result is a 3-tuple: (data, template_data_coroutine, templates)
  2. Access immediate data:
     - data["rows"], data["columns"], data["primary_keys"], data["primary_key_values"], data["units"]
     - Optionally, data.get("foreign_key_tables") may be present when requested via _extras.
  3. Render-time (in template runner):
     - template_context = await template_data_coroutine()
       - Contains "display_columns", "display_rows", "foreign_key_tables", "private", "custom_table_templates", and "metadata".
  4. Pick an appropriate template from templates (first matching file) and render it with combined context from data and template_context.

Notes:
- To include the foreign-key summary in the immediate data dict (so the renderer can avoid awaiting template_data), make sure the incoming request querystring contains _extras=foreign_key_tables.
- When foreign keys exist, each returned foreign-key dict will include "count" and "link" (link is built by appending ?<column>=<pk> to the URL returned by self.ds.urls.table).

Implementation hints for re-implementation:
- Ensure urlsafe_components and tilde_decode are applied to route-encoded path components prior to lookup.
- Use _sql_params_pks(db, table, pk_values) to produce SQL, params, and pks — this ensures correct handling of tables with no declared PK (rowid fallback).
- Use results.description to derive column names and results.rows to retrieve row tuples (matching the expectations of display_columns_and_rows).
- template_data must be an async zero-argument function (coroutine) so the caller can defer or avoid expensive display transformations until necessary.

### `datasette.views.row.RowView.data` · *method*

## Summary:
Fetches a single row from a table (based on URL primary key components), enforces visibility permissions, builds the raw data payload for templates, and returns an async template-data provider plus the preferred template names.

## Description:
This method is invoked during the request-handling pipeline when rendering a single-row view for a table. In Datasette's view pattern it is called by the RowView / DataView layer to obtain the data and auxiliary template data required to render a row.html (or database/table-specific) template.

Callers / lifecycle stage:
- Called from the view-rendering path when a request targets a single-record row URL (the route that includes database, table and pks in request.url_vars). The view layer uses the returned (data, template_data, templates) triplet to render the final response.

Why this is its own method:
- It encapsulates the steps of permission checking, PK parsing, SQL generation for the specific primary key(s), executing a targeted query, and preparing both immediate data and a lazily-evaluated template-data coroutine. Keeping this logic in a dedicated method separates data retrieval/preparation from transport and rendering concerns, enabling reuse, easier testing, and deferred template-specific processing.

## Args:
    request (object): The incoming request-like object expected to provide:
        - url_vars (dict-like): must contain "database" (route-encoded string), "table" (route-encoded string), and "pks" (route-encoded primary-key path).
        - args (dict-like or multidict): querystring parameters; used to check the "_extras" flag.
        - actor (object): the actor/identity used by permission checks.
      The method only requires these attributes and will raise NotFound/Forbidden if they do not correspond to valid resources or permissions.
    default_labels (bool): Optional flag (defaults to False). Present in the signature but not used by this implementation; callers may set it but it has no effect.

## Returns:
    tuple: (data, template_data, templates)
    - data (dict): immediate data dictionary containing:
        - "database" (str): database name (db.name) resolved from the route.
        - "table" (str): table name.
        - "rows" (list[tuple]): raw rows returned from the DB execute call (each row is an iterable/sequence of column values).
        - "columns" (list[str]): list of column names in the same order as in rows (derived from results.description).
        - "primary_keys" (list[str]): list of primary key column names used for the query (["rowid"] if table has no declared PKs).
        - "primary_key_values" (list[str]): the parsed URL-safe primary key components (from urlsafe_components).
        - "units" (dict): units metadata for the table (from self.ds.table_metadata(database, table).get("units", {})).
        - optionally "foreign_key_tables" (list/dict): included only if the request querystring _extras contains "foreign_key_tables" — otherwise, this key is absent in the returned data dict (the lazily-provided template_data still includes it).
    - template_data (callable coroutine): an async zero-argument coroutine function which, when awaited, returns a dict intended for template rendering with keys:
        - "private" (bool): whether the resource is private (from permission check).
        - "foreign_key_tables": result of self.foreign_key_tables(database, table, pk_values) — a structure describing related foreign-key rows.
        - "display_columns" (list[dict]): column metadata for display produced by display_columns_and_rows; this method also forces each column dict's "sortable" to False.
        - "display_rows" (list[Row]): display-ready row objects produced by display_columns_and_rows.
        - "custom_table_templates" (list[str]): prioritized template names that the templating layer can try (database- and table-specific first, then a fallback).
        - "metadata" (dict): table metadata from self.ds.metadata("databases") -> database -> "tables" -> table, or None/{} if missing.
    - templates (tuple[str, ...]): ordered template name candidates to render this view, e.g. ("row-{db}-{table}.html", "row.html"). Each name will have database/table names converted to CSS-safe form via to_css_class.

## Raises:
    NotFound: 
        - If the requested database route does not map to a Datasette database (caught and raised when get_database(route=...) fails).
        - If the constructed SQL query returns no rows (record not found for the provided PK components).
    Forbidden:
        - If the permission check via self.ds.check_visibility(...) indicates the actor may not view this table (visible is False).
    QueryInterrupted (or other db execution exceptions):
        - A db.execute(sql, params, truncate=True) call may raise database-level exceptions (QueryInterrupted is imported in the module and may be propagated). Such exceptions are not caught here and will propagate to the caller.

## State Changes:
    Attributes READ:
        - self.ds: used to resolve databases, metadata and table metadata, and to run a visibility check.
        - self.foreign_key_tables: method invoked to obtain related foreign-key rows (called from the inner template_data coroutine and possibly added to data).
    Attributes WRITTEN:
        - None. This method does not modify attributes on self.

## Constraints:
    Preconditions:
        - request.url_vars must contain the keys "database", "table", and "pks" (route-encoded strings).
        - self.ds must be present and implement:
            - get_database(route=...) -> database object with .name and methods used below.
            - check_visibility(actor, permissions=...) -> coroutine returning (visible:bool, private:bool).
            - table_metadata(database, table) and metadata(namespace) accessors used for units and template metadata.
        - The resolved database object must implement:
            - primary_keys(table) used indirectly by _sql_params_pks and display_columns_and_rows.
            - execute(sql, params, truncate=True) which returns an object with .description and .rows attributes.
    Postconditions:
        - The returned data dict contains raw DB rows, columns, primary key info, and units metadata.
        - The returned template_data coroutine will produce display-ready columns/rows and foreign-key information when awaited.
        - If control returns normally (no exceptions), then permission checks have passed and at least one row matching the provided PKs exists.

## Side Effects:
    - Performs database I/O:
        - Calls self.ds.get_database(route=...) to resolve the database.
        - Calls self.ds.check_visibility(...) to evaluate view permissions.
        - Calls _sql_params_pks(...) to build a parameterized SQL query.
        - Executes a targeted SELECT via db.execute(sql, params, truncate=True) to fetch the row(s).
        - Potentially calls self.foreign_key_tables(...) (which may execute additional queries) either immediately (if _extras contains "foreign_key_tables") or lazily inside template_data when awaited.
    - No external state is mutated by this method (no writes to disk or modifications of self attributes).

### `datasette.views.row.RowView.foreign_key_tables` · *method*

## Summary:
Return information about tables that have incoming foreign keys referencing a single-row primary key, including the number of matching rows in each foreign table and a URL linking to that filtered table view. Does not modify object state.

## Description:
This asynchronous helper is used when rendering a single-row detail page to find and present other tables that reference the current row via foreign keys. It:
- Queries the database for counts of rows in each referencing (foreign) table that match the provided primary key value.
- Builds a link for each foreign table that points to the table view filtered by the referencing column and the primary key.
- Returns a list of foreign-key metadata dictionaries augmented with two additional keys: "count" (int) and "link" (str).

Known callers and context:
- Intended to be invoked by view-rendering code in RowView (or other row-detail handlers) during the construction of a row detail page to display "referenced by" / "incoming foreign keys" information. It runs in the request-handling lifecycle (an async view pipeline) where self.ds and self.ds.databases are already available.
- Separated into its own method because it encapsulates: (1) database retrieval of foreign-key metadata, (2) building and executing a single SQL query that returns counts for each incoming foreign key, and (3) uniform construction of link URLs. This keeps the row-rendering code concise and isolates error handling (QueryInterrupted) and URL construction.

## Args:
    database (str): Name/key of the database inside self.ds.databases. Must refer to a valid database entry accessible as self.ds.databases[database].
    table (str): Table name (string) in the given database whose incoming foreign keys should be inspected.
    pk_values (list[str]): Sequence of primary-key value components for the current row. This method only supports single-column primary keys; when len(pk_values) != 1 the method immediately returns an empty list.

## Returns:
    list[dict]: A list of dictionaries, one per incoming foreign-key relationship. Each returned dict contains the original foreign-key metadata (the keys present in the entries returned by the database's get_all_foreign_keys result for incoming keys) plus:
        - "count" (int): Number of rows in the foreign table where the foreign column equals the provided primary-key value. Zero when none match.
        - "link" (str): A URL string pointing to the foreign table view filtered by the foreign column equal to the current primary-key value(s). Format: "<table_url>?<column>=<comma-joined pk values>". Note: if the foreign column name begins with an underscore, the column name in the query parameter will have "__exact" appended.
    Edge-case return values:
        - Returns [] immediately if len(pk_values) != 1
        - Returns [] when there are no incoming foreign keys for the table
        - Returns [] when a QueryInterrupted is raised during the count query
        - For each foreign key, "count" is 0 if the SQL query returns NULL/missing value for that relationship

## Raises:
    KeyError: If the provided database key is not present in self.ds.databases or the provided table key is not present in the mapping returned by db.get_all_foreign_keys(), those lookups will raise KeyError. (The method does not explicitly catch KeyError.)
    Any exception raised by self.ds.urls.table(...) or by db.execute(...) other than QueryInterrupted will propagate to the caller. QueryInterrupted is explicitly caught and results in an empty list return instead of being raised.

## State Changes:
    Attributes READ:
        - self.ds (accessed to obtain databases and urls helpers)
        - self.ds.databases[database] (the database object referenced as db)
        - db.get_all_foreign_keys() (called and awaited)
        - db.execute(sql, params) (called and awaited)
        - self.ds.urls.table(database, table_name) (used to construct links)
    Attributes WRITTEN:
        - None. The method does not modify attributes on self or other long-lived objects.

## Constraints:
    Preconditions:
        - pk_values must be an iterable of strings; the method only processes when len(pk_values) == 1.
        - self.ds and self.ds.databases must be initialized and contain the named database.
        - db.get_all_foreign_keys() must return a mapping where all_foreign_keys[table]["incoming"] yields an iterable of foreign-key descriptor dicts. Each foreign-key dict is expected to contain at least the keys "other_table" and "other_column".
    Postconditions:
        - If the method returns a non-empty list, each item is a dict containing the original fk metadata plus:
            - "count" set to an integer >= 0
            - "link" set to a non-empty string URL that encodes the filtering on the foreign column
        - The method never raises QueryInterrupted; that condition results in an immediate return of [].

## Side Effects:
    - Performs a synchronous effect on the database by executing a SELECT count(*) subqueries SQL statement via db.execute; this is a read-only operation (no modifications).
    - No external I/O beyond the database query and URL construction.
    - Does not mutate self or the db object (other than any internal temporary locals).
    - May propagate other exceptions from db.execute or self.ds.urls.table to the caller.

