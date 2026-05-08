# `url_builder.py`

## `datasette.url_builder.Urls` · *class*

## Summary:
A small helper that builds canonical application URLs for a Datasette instance and returns them as PrefixedUrlString values.

## Description:
Urls centralizes URL construction for common Datasette routes (instance root, static assets, database/table/query/row routes, logout, plugin static files, and blob access). Instantiate this class with a running Datasette-like object that provides:
- a setting(name: str) -> str method (used with "base_url") to obtain the application base path prefix, and
- a get_database(name_or_object) -> DatabaseLike method that returns an object exposing a .route attribute used as the database route string.

Motivation:
- Keep URL-building logic in one place so route formatting, base URL prefixing, and format-handling are consistent across the codebase.
- Return type is PrefixedUrlString (a thin subclass of str) so code that relies on string methods continues to work while preserving the "prefixed" string type.

When to instantiate:
- One Urls instance per Datasette-like object (typically created during Datasette initialization and stored on the Datasette instance as an attribute for reuse).
- Known callers: any request handlers or template renderers that need canonical URLs for resources, database routes, or record-level actions.

## State:
- ds (attribute)
  - Type: Datasette-like object (any object exposing at least .setting(name: str) and .get_database(name) methods)
  - Constraints: Must be provided at construction time and remain available for the lifetime of the Urls instance.
  - Invariant: ds is not modified by Urls; Urls methods call into ds to obtain live configuration or database route details.

Return types and related utilities (used by methods):
- PrefixedUrlString (str subclass)
  - Behaves like a normal string but preserves subclass on many string operations and in concatenation.
- path_with_format(request=None, path=None, format=None, extra_qs=None, replace_format=None)
  - Appends or encodes format (either as an extension like ".json" or as a _format query param) and merges query string parameters if necessary.
- tilde_encode(s: str) -> str
  - Produces tilde-encoded form of a path component (e.g., "/foo/bar" -> "~2Ffoo~2Fbar") and is used to encode database routes and table/query names embedded in path segments.

## Lifecycle:
- Creation:
  - Instantiate with a Datasette-like object: Urls(ds)
    - Required argument:
      - ds: object with methods setting(name: str) -> str and get_database(name) -> object with .route attribute.
- Usage:
  - Methods are stateless with respect to Urls; typical sequence is:
    1) Call instance(), database(), table(), query(), row(), static(), static_plugins(), logout(), or row_blob() as needed to build URLs.
    2) Use returned PrefixedUrlString values directly in templates, redirects, or HTTP responses.
  - There is no required ordering between methods — they are independent helpers. Some methods call others internally (e.g., table() uses database()) but callers do not need to call them in a specific order.
- Destruction:
  - No cleanup required. Urls holds only a reference to ds; it does not open resources or require closing.

## Methods (behavioral summary)
- __init__(ds)
  - Stores ds on self.ds for subsequent calls.

- path(path, format=None)
  - Args:
    - path (str | PrefixedUrlString): path fragment or already-prefixed PrefixedUrlString.
    - format (str | None): optional format name (e.g., "json", "csv") to be applied via path_with_format.
  - Behavior:
    - If path is an instance of PrefixedUrlString: treat it as already-prefixed; do not prepend base_url.
    - Otherwise:
      - If path starts with "/" strip the leading slash.
      - Prefix path with self.ds.setting("base_url") (the Datasette base URL string).
    - If format is not None: call path_with_format(path=path, format=format) to add the extension or _format query parameter.
    - Return a PrefixedUrlString instance wrapping the final path.
  - Return: PrefixedUrlString

- instance(format=None)
  - Same as path("", format=format). Returns URL for the application root (base_url) with optional format.

- static(path)
  - Builds "-/static/{path}" and passes through path(); returns the PrefixedUrlString for a static asset.

- static_plugins(plugin, path)
  - Builds "-/static-plugins/{plugin}/{path}" and passes through path(); returns the PrefixedUrlString for a plugin static asset.

- logout()
  - Returns path("-/logout") as a PrefixedUrlString.

- database(database, format=None)
  - Args:
    - database: identifier used by ds.get_database to look up a Database-like object.
    - format: optional format to pass to path_with_format.
  - Behavior:
    - Calls db = self.ds.get_database(database), expects db to have attribute .route (string) representing the database route (e.g., "/foo" or an empty string).
    - Encodes db.route using tilde_encode and passes it to path(..., format=format).
  - Return: PrefixedUrlString

- table(database, table, format=None)
  - Builds "{database_url}/{tilde_encode(table)}" where database_url is produced by self.database(database).
  - If format provided, ensures format is applied via path_with_format; returns PrefixedUrlString.

- query(database, query, format=None)
  - Similar to table(), but the second path component is tilde_encode(query) (for saved queries or query names). Returns PrefixedUrlString.

- row(database, table, row_path, format=None)
  - Builds "{table_url}/{row_path}" (row_path is used verbatim, not tilde-encoded) and optionally applies format. Returns PrefixedUrlString.

- row_blob(database, table, row_path, column)
  - Returns the table URL with an appended "/{row_path}.blob?_blob_column={quoted_column_name}" suffix.
  - column is URL-quoted using urllib.parse.quote_plus before inclusion into the query string.
  - Result preserves PrefixedUrlString type because PrefixedUrlString implements concatenation that returns its subclass.

## Method Map:
flowchart LR
    A[instance(format)] --> B[path]
    C[static(path)] --> B
    D[static_plugins(plugin,path)] --> B
    E[logout] --> B
    F[database(database,format)] --> B
    G[table(database,table,format)] --> F
    H[query(database,query,format)] --> F
    I[row(database,table,row_path,format)] --> G
    J[row_blob(database,table,row_path,column)] --> G

(Note: B represents the central path(...) helper used by many methods.)

## Raises:
- Urls.__init__: does not explicitly raise exceptions. If ds is missing required methods, AttributeError will be raised when methods are invoked.
- path(): does not raise explicitly. Underlying utilities may raise on misuse:
  - If ds.setting("base_url") returns a non-string that cannot be concatenated with path, TypeError may occur.
  - path_with_format (invoked when format is provided) will perform string operations and URL-encoding; misuse of its parameters may raise builtin exceptions (TypeError) but Urls does not itself raise custom exceptions.
- database(): if self.ds.get_database(database) raises (e.g., database not found), the exception is propagated unchanged.

## Example (typical usage sequence):
1) Create Urls:
   urls = Urls(ds)
   - ds must implement: ds.setting(name: str) and ds.get_database(name)

2) Build instance root:
   root_url = urls.instance()                  -> PrefixedUrlString for base_url
   root_json = urls.instance(format="json")    -> PrefixedUrlString with .json or _format

3) Static asset:
   css_url = urls.static("css/site.css")       -> PrefixedUrlString for "-/static/css/site.css" under base_url

4) Database/table/query/row:
   db_url = urls.database("example")           -> PrefixedUrlString for the database route (tilde-encoded)
   table_url = urls.table("example", "users")  -> PrefixedUrlString for users table route
   row_url = urls.row("example", "users", "1") -> PrefixedUrlString for a specific row

5) Blob access:
   blob_url = urls.row_blob("example", "users", "1", "avatar")
   -> PrefixedUrlString like "<base>/example_route/users/1.blob?_blob_column=avatar"

No explicit cleanup is required.

### `datasette.url_builder.Urls.__init__` · *method*

## Summary:
Store the Datasette-like instance on the Urls helper so all URL-building methods can access application configuration and database routes.

## Description:
Known callers and lifecycle stage:
- Called during Datasette initialization when constructing a Urls helper instance (typical usage: urls = Urls(ds)).
- Consumers are request handlers, template renderers, and other runtime code that need to build canonical URLs; they obtain the Urls instance from the Datasette instance or its attributes.
- This method is invoked at object construction time (creation phase of the Urls lifecycle).

Why this logic is a separate method:
- Keeps object construction explicit and minimal (single responsibility): the constructor simply records the dependency (ds) so other Urls methods can be lightweight and stateless.
- Separating the assignment into an explicit __init__ enables dependency injection for testing and makes the dependency contract (what Urls requires from ds) clear.

## Args:
    ds (object): Required. A Datasette-like object that Urls will hold as a live reference.
        - Expected interface:
            * setting(name: str) -> str
            * get_database(name_or_object) -> DatabaseLike (object exposing a .route attribute)
        - No default. Passing None is allowed at runtime but will lead to errors when Urls methods are used.

## Returns:
    None

## Raises:
    None explicitly. The constructor does not perform validation and therefore does not raise custom exceptions.
    - Note: If attribute assignment fails due to a non-standard target object that overrides __setattr__, a propagated exception (e.g., AttributeError, TypeError) could occur; this is not specific to Urls.

## State Changes:
    Attributes READ:
        - None
    Attributes WRITTEN:
        - self.ds (set to the ds argument)

## Constraints:
    Preconditions:
        - Caller should supply a Datasette-like object implementing at least the methods documented above (setting and get_database). While __init__ does not validate these methods, many Urls methods assume their presence and will raise if they are missing.
    Postconditions:
        - After return, self.ds is a direct reference to the provided ds object (identity preserved).
        - No additional initialization or side-effect is performed.

## Side Effects:
    - Mutates only the Urls instance by assigning to self.ds.
    - No I/O, network calls, or global state mutation occur.
    - No validation or eager calls into ds are performed at construction time.

### `datasette.url_builder.Urls.path` · *method*

## Summary:
Constructs a base-relative URL string and returns it as a PrefixedUrlString, optionally applying a response format. Does not mutate the Urls object.

## Description:
This method centralizes the logic for turning a provided path into a full, base-url-prefixed URL string and wrapping it in PrefixedUrlString so concatenation and other string operations preserve the subclass type.

Known internal callers:
- Urls.instance (generates the site root URL)
- Urls.static (static asset URLs)
- Urls.static_plugins (plugin static assets)
- Urls.logout (logout URL)
- Urls.database (database route builder)

Typical usage stage:
- Invoked during URL construction for responses, templates, and link generation inside the Urls helper. It is separated into its own method so all places that need the base_url prefix and optional format handling use a single, consistent implementation and to ensure the returned string is the PrefixedUrlString subclass.

## Args:
    path (str | PrefixedUrlString):
        The path to convert into a full URL. If this is already a PrefixedUrlString, the method treats it as already-prefixed and skips adding the base URL.
        Expected to be textual (a str or PrefixedUrlString). If given a non-textual object, built-in string operations used here (startswith) may raise an exception.
    format (str | None, optional):
        If provided, passed to path_with_format to either append a file-extension-style suffix (e.g., .json) or add an _format query parameter per path_with_format's rules. Any non-empty string is accepted; None means "no format adjustment". Default is None.

## Returns:
    PrefixedUrlString:
        A PrefixedUrlString (subclass of str) representing the resulting URL path. Behavior specifics:
        - If the input path was not a PrefixedUrlString, the return value is the base_url (from self.ds.setting("base_url")) concatenated with the provided path (after removing a single leading slash, if present).
        - If format is provided, the returned string will include the format either as a file extension or as an _format query parameter according to path_with_format.
        - If the input is already a PrefixedUrlString, the same logical string (possibly adjusted by path_with_format) is returned as a PrefixedUrlString.

## Raises:
    AttributeError:
        If self.ds has no attribute/method named setting, calling self.ds.setting("base_url") will raise AttributeError.
    Exception (propagated from dependencies):
        Any exception raised by self.ds.setting("base_url") or path_with_format (for example, TypeError if arguments are of incorrect types) will propagate out of this method. The method itself does not wrap or convert exceptions.

## State Changes:
    Attributes READ:
        self.ds (used to call self.ds.setting("base_url"))
    Attributes WRITTEN:
        None — this method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - self.ds must be an object exposing a callable setting(name) that returns a base URL string when called with "base_url".
        - path should be a text-like object (str or PrefixedUrlString). If it is not a PrefixedUrlString, it must support startswith("/") and string concatenation with the base_url.
    Postconditions:
        - The returned value is a PrefixedUrlString whose string value:
            * begins with the base_url (if the input path was not a PrefixedUrlString),
            * has no leading "/" from the original path (a single leading slash is removed before concatenation),
            * includes the requested format if format was provided (as defined by path_with_format).
        - The Urls object (self) remains unchanged.

## Side Effects:
    - Calls self.ds.setting("base_url") to obtain the base URL string (a read-only access to ds).
    - Calls path_with_format(path=..., format=format) when format is not None; path_with_format may examine or combine query strings but performs no external I/O.
    - No network, filesystem, or other external I/O is performed by this method itself.

### `datasette.url_builder.Urls.instance` · *method*

## Summary:
Return a PrefixedUrlString representing the Datasette instance root URL by delegating to the shared path builder; does not mutate the Urls object.

## Description:
This is a thin convenience method that delegates to Urls.path with an empty path string and an optional format argument. The implementation is a single delegation: return self.path("", format=format). Because Urls.path performs base URL prefixing and optional format suffixing (via self.ds.setting("base_url") and path_with_format), calling instance(...) yields a PrefixedUrlString for the instance root with the same normalization and formatting behavior as other URL builders in this class.

Known callers:
- No callers are defined inside this file. Call sites elsewhere in the codebase may call this method when they need the canonical instance root URL, but those callers are not enumerated here.

Why this is a separate method:
- Encapsulates the common operation "build the root (empty) path with optional format" so callers do not need to pass an explicit empty string every time and to keep intent explicit.

## Args:
    format (str | None): Optional format specifier forwarded to Urls.path. If not None, Urls.path will call path_with_format(path=..., format=format) before wrapping the final value in a PrefixedUrlString. Default: None.

## Returns:
    PrefixedUrlString: A PrefixedUrlString instance produced by Urls.path for the empty path. The returned value corresponds to the computed path after:
      - optionally prefixing with self.ds.setting("base_url") (since an empty string is not a PrefixedUrlString, Urls.path will prepend base_url), and
      - optionally applying path_with_format when format is not None.

## Raises:
    This method does not raise its own errors, but it will propagate any exceptions raised by Urls.path or the utilities it calls. Concretely, callers may observe exceptions originating from:
      - self.ds.setting("base_url") (if self.ds is missing or its setting method raises),
      - path_with_format (if given an invalid format),
      - PrefixedUrlString construction (if the wrapper raises on invalid input).

## State Changes:
Attributes READ:
    self.ds — accessed indirectly by Urls.path to obtain the "base_url" setting via self.ds.setting("base_url").
    self.path (method) — invoked to perform the actual construction.

Attributes WRITTEN:
    None — this method does not modify any attributes on self or external objects.

## Constraints:
Preconditions:
    - self is an initialized Urls instance with a valid self.ds attribute exposing a setting(name) method.
    - format is either None or an acceptable argument for path_with_format (typically a string).

Postconditions:
    - No mutation of self occurs.
    - The return value is a PrefixedUrlString wrapping the path computed by Urls.path for the empty path and the provided format.

## Side Effects:
    - No I/O or network calls are performed by this method directly.
    - May cause reads of configuration/state via self.ds.setting("base_url") during the delegated Urls.path call.
    - No external object is mutated by this method itself.

### `datasette.url_builder.Urls.static` · *method*

## Summary:
Constructs a URL for a static asset by prefixing the provided path with the internal "-/static/" fragment and delegating to the Urls.path builder; returns a PrefixedUrlString representing the fully-prefixed URL.

## Description:
This method exists to centralize the common pattern of building URLs that point to Datasette's static assets. It composes the static path fragment ("-/static/{path}") and delegates to Urls.path to apply the application's base_url and optional format handling consistently.

Known callers and lifecycle stage:
- No explicit callers are defined in this file; typically invoked when templates, response builders, or code generating links to static assets need a canonical URL for a static file (CSS, JS, images, plugin static files that are not in plugins-specific directories, etc.). It is called during URL construction for rendering responses or embedding asset links.

Why this is a separate method:
- Provides a concise, self-documenting API for static asset URLs.
- Ensures every static asset URL goes through Urls.path so the application's base_url and formatting rules are applied consistently.
- Keeps calling code concise (templates and renderers can call urls.static("...") rather than duplicating the "-/static/" prefix).

## Args:
    path (str):
        The path to the static asset relative to Datasette's static root (for example "app.css" or "images/logo.png").
        - Expected type: textual (str). Note: passing a PrefixedUrlString is allowed but will be coerced to str by Python's f-string formatting before delegation to Urls.path.
        - No default; required.

## Returns:
    PrefixedUrlString:
        A PrefixedUrlString (a subclass of str) representing the resulting URL. In practice:
        - The returned string value is produced by Urls.path called with the argument "-/static/{path}".
        - Since Urls.path prepends the configured base_url when given a plain str, the returned value will normally begin with the application's base_url followed by "-/static/{path}".
        - The return value is the PrefixedUrlString wrapper returned by Urls.path (so callers can rely on string operations and concatenation behavior of that subclass).

## Raises:
    AttributeError:
        If self.ds does not expose a callable setting method and Urls.path attempts to call self.ds.setting("base_url").
    Any exception raised by Urls.path or its dependencies:
        - For example, TypeError if path_with_format (if later used) receives invalid types, or other exceptions propagated from self.ds.setting or path_with_format.
    Note: static does not catch exceptions; it forwards whatever Urls.path would raise.

## State Changes:
    Attributes READ:
        - Via delegation to Urls.path: self.ds (used when Urls.path calls self.ds.setting("base_url")).
    Attributes WRITTEN:
        - None. This method does not modify attributes on self.

## Constraints:
    Preconditions:
        - self must be an instance of Urls with a working path method that accepts a single path argument and returns a PrefixedUrlString.
        - self.ds (the Datasette instance attached to Urls) should provide a setting(name) method that returns the base_url when requested; otherwise Urls.path may raise.
        - The supplied path argument must be convertible to a string (str(path) must succeed); f-string interpolation will convert non-str inputs using __format__/__str__.
    Postconditions:
        - The returned PrefixedUrlString is equivalent to calling self.path("-/static/" + str(path)).
        - Because the fragment passed to path always begins with "-", Urls.path will not strip a leading "/" from the fragment; no normalization of inner slashes is performed by static itself.
        - If the caller supplied a PrefixedUrlString as the path argument, it is coerced to a str within the f-string, so the result will be processed as a plain path by Urls.path (i.e., it will not be treated as already-prefixed).

## Side Effects:
    - Delegates to Urls.path which reads configuration via self.ds.setting("base_url"); static itself performs no I/O.
    - No writes to disk, network calls, or mutations of objects outside self are performed by this method.
    - Behaves as a pure helper that builds and returns a string-like URL value.

## Examples:
    Given a Datasette instance whose base_url is "/":
        urls.static("app.css") -> PrefixedUrlString("/") + "-/static/app.css" -> "/-/static/app.css"
    Important edge-case example:
        urls.static("/icons/favicon.ico") -> Produces "/-/static//icons/favicon.ico" (double slash preserved; static does not remove slashes inside the provided path fragment)

### `datasette.url_builder.Urls.static_plugins` · *method*

## Summary:
Builds and returns a PrefixedUrlString for a plugin static asset by composing the path segment "-/static-plugins/{plugin}/{path}" and delegating to Urls.path so the configured base_url is applied.

## Description:
Known callers and context:
    - Intended to be used by templates, view handlers, or any code that needs a canonical URL to a plugin-provided static asset (CSS, JS, images) during request rendering or when generating responses.
    - Lifecycle stage: invoked at URL-generation time (e.g., while rendering an HTML page or emitting a JSON response that includes links).

Why this is a separate method:
    - Encapsulates the canonical path pattern for plugin static assets so callers don't duplicate the literal "-/static-plugins/..." segment.
    - Keeps callers simple by delegating base_url handling and wrapping to Urls.path.

## Args:
    plugin (str): Plugin identifier (slug/name) included in the URL path. Expected to be a short identifier without leading/trailing slashes.
    path (str): Relative path within the plugin's static directory (e.g. "css/main.css" or "images/icon.png"). Treated as a path fragment; this method does not normalize or URL-encode this fragment.

## Returns:
    PrefixedUrlString: A PrefixedUrlString wrapping the final path. The underlying string is produced by Urls.path and will consist of:
        [base_url from self.ds.setting("base_url")] + "-/static-plugins/{plugin}/{path}"
    Example:
        If self.ds.setting("base_url") == "/",
        plugin == "myplugin",
        path == "css/style.css",
        the method returns PrefixedUrlString("/-/static-plugins/myplugin/css/style.css").

    Edge cases:
        - The method does not URL-encode plugin or path. Characters that require URL-escaping must be handled by the caller.
        - If plugin or path contain embedded slashes (including a leading slash in the path argument), the resulting URL may contain consecutive slashes (e.g., ".../myplugin//file"). Urls.path will only strip a leading slash from the entire path string if it begins with "/", which does not occur here because the constructed string begins with "-/...".

## Raises:
    - This method itself does not raise custom exceptions.
    - It will propagate exceptions thrown by Urls.path or by self.ds.setting("base_url") invoked within Urls.path (for example, configuration access errors).

## State Changes:
Attributes READ:
    - self.ds (indirectly) — via Urls.path which calls self.ds.setting("base_url")
    - self.path method (call) — uses Urls.path behavior

Attributes WRITTEN:
    - None. The method does not mutate self or external objects.

## Constraints:
Preconditions:
    - self is an initialized Urls instance with a functioning path method and a ds attribute exposing setting("base_url").
    - plugin and path are provided as strings (or objects convertible to strings). The method does not validate or sanitize them.

Postconditions:
    - Returns a PrefixedUrlString whose underlying string is the base_url-prefixed "-/static-plugins/{plugin}/{path}".
    - No attributes on self are modified.

## Side Effects:
    - No I/O or network calls.
    - No mutation of objects outside self.
    - Calls Urls.path which reads configuration via self.ds.setting("base_url") and constructs a PrefixedUrlString instance.

### `datasette.url_builder.Urls.logout` · *method*

## Summary:
Produces the Datasette instance's logout URL by delegating to the shared path construction logic and returning it as a PrefixedUrlString.

## Description:
This is a tiny convenience method that centralizes the canonical logout path ("-/logout") and hands it to Urls.path so the instance base URL, optional formatting, and PrefixedUrlString wrapping are applied uniformly.

Known callers and context:
- Typically called from presentation or response-generation code: templates that render a "Logout" link, view handlers that redirect users to sign-out, or helper functions that build navigation menus.
- It is invoked at URL-construction time (rendering/response stage), not during startup or database access code.

Why this logic is a separate method:
- Avoids scattering the literal "-/logout" string across the codebase.
- Lets callers rely on Urls.path to handle base URL prefixing and any future URL-formatting behavior without changing call sites.
- Keeps templates and redirect code concise and intention-revealing.

## Args:
- None

## Returns:
- PrefixedUrlString
  - Semantics: the return value is the PrefixedUrlString instance produced by Urls.path when given the literal path "-/logout".
  - Under the hood (per Urls.path): if the provided path is not already a PrefixedUrlString, Urls.path will remove any leading "/" from the path, then prepend self.ds.setting("base_url") to it, and finally wrap the result in PrefixedUrlString. Therefore the wrapped string content will be self.ds.setting("base_url") + "-/logout".
  - Edge cases:
    - The exact characters between base_url and "-/logout" depend on the value of base_url (e.g., whether it ends with a trailing "/"), because Urls.path concatenates base_url and the path directly after stripping a leading "/" from the given path.
    - No format argument is accepted by logout itself; Urls.path's format handling is not used here.

## Raises:
- logout does not raise directly.
- Exceptions may propagate from Urls.path or from self.ds.setting("base_url") calls:
  - AttributeError if self.ds is missing or does not expose setting(...)
  - Any exception raised by ds.setting(...)
  - TypeError during concatenation if ds.setting("base_url") returns a non-string (since Urls.path performs string concatenation)

## State Changes:
- Attributes READ:
  - self.ds (indirectly; Urls.path calls self.ds.setting("base_url"))
- Attributes WRITTEN:
  - None

## Constraints:
- Preconditions:
  - The Urls object must have been initialized with a ds that provides a setting(name: str) -> str interface so that Urls.path can read "base_url".
  - Callers should treat the result as a PrefixedUrlString (not assume a plain str).
- Postconditions:
  - Returns a PrefixedUrlString whose internal string equals self.ds.setting("base_url") + "-/logout" (after Urls.path removes any leading "/" from "-/logout" — which has no effect here — and wraps the result).

## Side Effects:
- None in terms of I/O or network activity. The method only constructs and returns a PrefixedUrlString. Any side effects are limited to what ds.setting(...) may perform (if that method has side effects), but logout itself performs no external actions.

## Examples (usage patterns):
- Template rendering: pass urls.logout() to template context to render an href for a logout link (the template/view code expects a PrefixedUrlString and will include it in an anchor's href).
- Redirect in a view: return a HTTP redirect to urls.logout() so the user is sent to the standardized sign-out endpoint.

Notes:
- Because Urls.path strips a leading "/" from provided paths before prefixing, providing "-/logout" (without a leading slash) is the intended literal value; the method preserves that literal in the final wrapped string.

### `datasette.url_builder.Urls.database` · *method*

## Summary:
Return a PrefixedUrlString representing the URL for the specified database, built from the database's route and optionally formatted.

## Description:
- Known callers and context:
    - Urls.table(database, table, format=None) calls this method to build the base URL for a table.
    - Urls.query(database, query, format=None) calls this method to build the base URL for a query.
    - Urls.row(database, table, row_path, format=None) and Urls.row_blob(...) indirectly use this method via Urls.table which calls database().
    - Typical lifecycle: invoked when constructing links/URLs for HTTP responses, templates, or API endpoints that reference a specific database within the Datasette instance.
- Why this is a separate method:
    - Centralizes the logic for resolving a database identifier into a route and converting it into a properly prefixed URL. Multiple Urls methods reuse this behavior (table, query, etc.), so extracting it avoids duplication and ensures consistent tilde-encoding and format handling.

## Args:
    database (Any): Value passed directly to self.ds.get_database(database). In typical usage this is a database name (str) or any identifier accepted by the Datasette instance's get_database method.
    format (str | None, optional): If provided, forwarded to self.path and will cause path_with_format to be applied (exact semantics depend on path_with_format). Defaults to None.

## Returns:
    PrefixedUrlString: A PrefixedUrlString instance representing the complete URL for the database route. The returned string is produced by Urls.path called with tilde_encode(db.route) (so the database route is tilde-encoded before being prefixed). If format is not None, the returned value will reflect the formatting applied by path_with_format through Urls.path.

## Raises:
    Propagates exceptions from:
        - self.ds.get_database(database): e.g., lookup/factory errors if the database cannot be resolved (exact exception types and conditions are determined by the Datasette instance).
        - self.path(...): any errors raised while constructing or formatting the path (for example, if path_with_format raises on invalid format).
    Note: This method does not perform its own error handling; callers should handle exceptions coming from get_database and path.

## State Changes:
    Attributes READ:
        - self.ds (used to call self.ds.get_database(database)); Urls.path may also read self.ds.setting("base_url") internally.
    Attributes WRITTEN:
        - None. This method does not modify attributes on self.

## Constraints:
    Preconditions:
        - self.ds must be a valid object exposing get_database(...) method.
        - The object returned by self.ds.get_database(database) must expose a .route attribute (string-like) that tilde_encode can accept.
    Postconditions:
        - Returns a PrefixedUrlString whose underlying path corresponds to Urls.path(tilde_encode(db.route), format=format). Concretely, when db.route is provided, the route will be tilde-encoded and then prefixed using the instance base URL (as implemented by Urls.path). If format is provided, path_with_format will be applied by Urls.path to reflect that format.

## Side Effects:
    - No I/O (network or disk) is performed by this method itself.
    - The method calls into self.ds.get_database(database) (which may perform internal lookups within the Datasette instance) and into Urls.path (which may read settings like base_url and call path_with_format). Any side effects or I/O from those calls are not introduced here but will be propagated.

### `datasette.url_builder.Urls.table` · *method*

## Summary:
Constructs and returns the URL path for a table endpoint (database + table), optionally applying a response format, and returns it wrapped as a PrefixedUrlString.

## Description:
- Known callers:
    - Urls.row — builds a row URL by calling Urls.table(...) then appending the row path.
    - Urls.row_blob — uses Urls.table(...) and appends blob-specific query parameters.
- Lifecycle / context:
    - Invoked during URL generation when the application needs the canonical path to a table page, e.g., while rendering links for table views or when constructing row/blob URLs that are anchored to a table.
- Rationale for being a dedicated method:
    - Centralizes the logic for combining the database route and the table name and for applying optional output formatting. This avoids duplication (row and row_blob reuse it) and ensures consistent tilde-encoding and format handling across callers.

## Args:
    database (Any):
        Value forwarded to Urls.database(database). This parameter accepts the same kinds of inputs that Urls.database accepts (typically a database name or a database object identifier that self.ds.get_database(...) supports).
    table (str):
        Table identifier/name. Will be passed through tilde_encode(...) so it may contain characters (including slashes) that require encoding for safe use inside the path.
    format (str | None, optional):
        Output format hint such as "json", "csv", etc. If provided, it is forwarded to path_with_format(...). Default is None (no format applied).

## Returns:
    PrefixedUrlString:
        A PrefixedUrlString instance containing the final URL path for the table. Typical forms:
        - "<base_url><db_route>/<tilde_encoded_table>" (when format is None)
        - "<base_url><db_route>/<tilde_encoded_table>.<format>" or
          "<base_url><db_route>/<tilde_encoded_table>?_format=<format>" (depending on existing path contents and path_with_format behavior)
        The returned value is a str subclass (PrefixedUrlString) so it behaves like a string but preserves the library's prefixed-url semantics.

## Raises:
    - No exception is explicitly raised by this method itself.
    - Exceptions raised by called functions may propagate:
        * Any exception from Urls.database(database) (for example from self.ds.get_database(...)).
        * Any exception from tilde_encode(table) (for example if a non-string that cannot be encoded is passed).
        * Any exception from path_with_format(...) when format is provided.
    The method does not catch or wrap these exceptions.

## State Changes:
- Attributes READ:
    - self.database (method) — called to obtain the database route for the supplied database argument.
    - (indirectly) self.ds — accessed by self.database (via Urls.database which calls self.ds.get_database(...)).
- Attributes WRITTEN:
    - None. The method does not modify self or any of its attributes.

## Constraints:
- Preconditions:
    - The value passed as database must be acceptable to Urls.database (i.e., something self.ds.get_database(...) can resolve).
    - table should be a string-like object (tilde_encode expects a str); non-string inputs may cause an exception in tilde_encode.
    - If format is provided it should be a string name of a format understood by the application (e.g., "json"), since it is forwarded to path_with_format.
- Postconditions:
    - The method returns a PrefixedUrlString representing the canonical path to the table. It does not mutate the Urls instance.
    - If format was provided, the returned path will reflect the format according to path_with_format rules (either a file-extension suffix or a _format query parameter, and possibly additional query string merging).

## Side Effects:
- No I/O or external network calls are performed by this method itself.
- It does call into Urls.database(...), which invokes self.ds.get_database(...) — that is an access to the Datasette data structures and may have side effects or raise errors depending on that implementation.
- No external objects (other than via return value) are mutated.

### `datasette.url_builder.Urls.query` · *method*

## Summary:
Constructs and returns a PrefixedUrlString for a query resource in a specific database without modifying the Urls instance.

## Description:
- Known callers and context:
    - There are no direct internal callers recorded in this module's stored summaries. In practice this method is used wherever the application needs a URL that represents a textual query for a given database — for example when rendering links in templates, building API response links, or generating saved-query URLs.
    - Lifecycle stage: invoked at URL-construction time during request handling or template rendering, when code needs a stable URL string referencing a query resource.
- Why this is its own method:
    - Encapsulates the canonical composition rule for query URLs (database base path + tilde-encoded query + optional format handling). Centralizing the logic avoids duplication and ensures consistent encoding and format behavior across the codebase.

## Args:
    database (Any):
        - Forwarded to self.database(database). Typically a database name (str) or other identifier accepted by the Datasette instance's get_database method.
        - No validation is performed here; resolution and validation occur inside self.database / self.ds.get_database.
    query (str):
        - The query string to place into the URL. Must be a Python str (tilde_encode expects a str).
        - Example values: "select * from x", "/path/with/slashes".
    format (str | None, optional):
        - If provided, forwarded to path_with_format to adjust the returned path (e.g., to add a suffix like ".json" or to force _format as a query parameter). Defaults to None.

## Returns:
    PrefixedUrlString
        - A PrefixedUrlString instance containing the final URL string.
        - Construction steps:
            1. Call self.database(database) to obtain the database base path (a PrefixedUrlString already prefixed with the instance base URL).
            2. Append "/" followed by tilde_encode(query) to that base path.
            3. If format is not None, call path_with_format(path=that_string, format=format) to apply format-specific adjustments.
            4. Wrap the resulting string with PrefixedUrlString(...) and return it.
        - Edge-case return behavior:
            - If query == "", tilde_encode("") returns the empty string, so the returned path will contain a trailing "/" immediately after the database base path (subject to further modification by format if provided).
            - If any of the steps raise an exception, no value is returned.

## Raises:
    - Propagates exceptions from:
        - self.database(database): e.g., errors from self.ds.get_database if the database cannot be resolved.
        - tilde_encode(query): will raise if query is not a str (the implementation calls s.encode("utf-8")).
        - path_with_format(path=..., format=format): any errors raised while applying format handling (for example, if format is of an inappropriate type).
    - This method does not catch exceptions; callers must handle errors raised by the called helpers.

## State Changes:
- Attributes READ:
    - self.database(...) (method call) — which in turn reads self.ds (uses self.ds.get_database and Urls.path that may read self.ds.setting("base_url")).
    - tilde_encode (pure function applied to the query string).
    - path_with_format (pure function applied when format is provided).
- Attributes WRITTEN:
    - None. The Urls instance and inputs are not mutated.

## Constraints:
- Preconditions:
    - self must be a valid Urls instance constructed with a Datasette-like object on self.ds exposing get_database and setting methods.
    - query must be a str. Passing other types may raise an exception inside tilde_encode.
    - database must be an identifier accepted by self.ds.get_database.
- Postconditions:
    - On successful return, self is unchanged.
    - The returned PrefixedUrlString's text equals: (database base path) + "/" + tilde_encode(query), with format handling applied if format was provided.

## Side Effects:
    - No direct I/O is performed by this method.
    - The method calls self.ds.get_database (via self.database), which may perform internal lookups inside the Datasette instance; any side effects from those calls are not introduced here but will be observed if present.
    - No mutation of external objects or global state occurs.

### `datasette.url_builder.Urls.row` · *method*

## Summary:
Builds and returns a PrefixedUrlString for a single row by joining the table URL and the given row_path, optionally applying an output format.

## Description:
This method composes a URL path that points to a specific row within a table. It calls self.table(database, table) to obtain the table URL (a PrefixedUrlString), appends "/" and the provided row_path, and — if a format is supplied — delegates to path_with_format(path=..., format=format) to apply the format. The final string is wrapped as a PrefixedUrlString and returned.

Known callers:
- No concrete call sites were present in the inspected memory snapshot. Conceptually, callers are components that render links to individual rows (views, templates, or plugins), or other URL-building helpers inside the application.

Why this is a separate method:
- Encapsulates the standard row path composition (table URL + "/" + row identifier) and the format-application step so callers do not duplicate this logic and so the behavior is consistent across the codebase.

## Args:
    database (str): Identifier for the database; passed through to self.table.
    table (str): Table name; passed through to self.table (which applies tilde-encoding).
    row_path (str): The path segment(s) identifying the row. Caller must provide any required URL-encoding; this method does not modify or quote row_path.
    format (str or None, optional): If provided, forwarded to path_with_format to apply an output format (e.g., "json", "csv"). Defaults to None.

## Returns:
    PrefixedUrlString: The constructed path wrapped in PrefixedUrlString. Typical forms:
        - Without format: "<base_url><db-route>/<table-name>/<row_path>"
        - With format and no dot in the path: "<...>/<row_path>.<format>"
        - With format and a dot anywhere in the path: "<...>/<row_path>?_format=<format>" (path_with_format may add a query parameter instead of an extension)
    Notes:
        - Because self.table returns a PrefixedUrlString and PrefixedUrlString.__add__ returns the same subclass, concatenation preserves the PrefixedUrlString type.
        - If row_path begins with "/" the resulting path will include a double slash between the table URL and row_path (no leading-slash stripping is performed).
        - The presence of a dot anywhere in the composed path (including in row_path) changes how format is applied (see Constraints).

## Raises:
    - Any exception raised by self.table(database, table); for example, if database/table resolution fails.
    - Any exception raised by path_with_format when format is supplied and invalid inputs are provided.
    This method does not raise additional exceptions itself.

## State Changes:
    Attributes READ:
        - self.table (method) — this method is called and thus may read self.ds or other state via self.table/self.database.
    Attributes WRITTEN:
        - None. The method does not mutate self or other objects.

## Constraints:
    Preconditions:
        - database and table must be valid inputs for self.table.
        - row_path must be a str (or str-like). If it contains characters that should be URL-escaped, the caller must provide an encoded value.
        - format, if provided, must be a format string acceptable to path_with_format.
    Exact behavior of format application (from path_with_format):
        - If the composed path contains a dot ('.') anywhere, path_with_format will NOT append ".{format}"; instead it will set a query parameter "_format" to the provided format (and merge with any existing query string).
        - If the composed path contains no dot, path_with_format will append ".{format}" to the path.
        - path_with_format will also merge or append extra query-string parameters deterministically (it URL-encodes sorted items).
    Postconditions:
        - Returns a PrefixedUrlString whose string value equals:
            str(self.table(database, table)) + "/" + row_path
          possibly transformed by path_with_format when format is supplied.
        - No attributes on self are modified.

## Side Effects:
    - None external: no network, file, or other I/O.
    - No mutation of objects outside self.
    - The only observable effect is the returned PrefixedUrlString value.

### `datasette.url_builder.Urls.row_blob` · *method*

## Summary:
Return the URL for retrieving a blob value for a given row and column, composed from the table URL plus a ".blob" endpoint and a URL-encoded _blob_column query parameter; this does not modify the Urls instance.

## Description:
This method composes the endpoint used to fetch the raw blob content for a particular row cell. It builds the URL by starting with the table URL returned by Urls.table(database, table), appending "/{row_path}.blob", and adding the _blob_column query parameter whose value is produced by urllib.parse.quote_plus(column).

Known callers and context:
- No concrete callers are present in the provided source fragment. In the Datasette codebase this kind of helper is typically used by templates or response-building code that needs to link to or redirect to raw blob content for a row (for example, rendering a link to download an image stored in a blob column, or constructing an API redirect to the raw blob).
- Invocation stage: URL construction / response building — called when the application generates links or endpoints for blob content.

Why this is a separate method:
- The URL pattern for serving a blob (table base + "/{row_path}.blob?_blob_column={column}") is a repeated format. Encapsulation centralizes encoding behavior for the column name (quote_plus) and keeps callers free from manual string formatting, reducing duplication and encoding errors.

## Args:
    database (str): Identifier for the database passed through to Urls.table. Must be valid for Datasette.get_database.
    table (str): Table name passed to Urls.table. It will be processed/encoded by Urls.table (tilde-encoding).
    row_path (str): Row path segment identifying the row within the table. Inserted verbatim into the path before ".blob" (this method does not URL-encode it).
    column (str): Column name whose blob should be served. Must be a string; it will be encoded using urllib.parse.quote_plus. Passing None or a non-string will raise a TypeError from quote_plus.

## Returns:
    str or PrefixedUrlString: The result of concatenating self.table(database, table) and the formatted string "/{row_path}.blob?_blob_column={quote_plus(column)}".
    - The concrete return type depends on the implementation of PrefixedUrlString.__add__:
        * If PrefixedUrlString.__add__ returns a PrefixedUrlString, this method returns a PrefixedUrlString.
        * If __add__ returns a plain str, this method returns a str.
    The returned value represents the full blob URL; callers may cast to str if a plain string is required.

Edge cases:
    - If column == "": the query parameter will be present as _blob_column= with an empty value.
    - If column contains spaces or special characters, quote_plus replaces spaces with '+' and percent-encodes other characters.
    - row_path is not encoded here — if it contains characters that must be percent-encoded in URLs, those characters will appear verbatim and may produce an invalid URL unless the caller provides an already-encoded row_path.

## Raises:
    TypeError: If column is None or not a string/bytes-like object accepted by urllib.parse.quote_plus.
    Any exception raised by Urls.table(database, table) is propagated. Typical propagated failures include:
        - Errors from Datasette.get_database when resolving database
        - Errors from tilde_encode or path_with_format invoked by Urls.table

## State Changes:
Attributes READ:
    - self.ds (indirectly) — accessed via Urls.table when resolving the database route/base URL.
Attributes WRITTEN:
    - None. This method performs no mutations on self or external objects.

## Constraints:
Preconditions:
    - database and table must be valid identifiers acceptable to the Datasette instance (so Urls.table can resolve them).
    - column must be a str (or bytes) acceptable to urllib.parse.quote_plus; callers should not pass None.
Postconditions:
    - The method returns a composed URL-like value containing the appended ".blob" path and a _blob_column query parameter whose value is the URL-encoded column string.
    - No internal state or external resources are modified.

## Side Effects:
    - No I/O, network, or external service interactions occur.
    - No external objects are mutated.
    - Only local string composition and URL quoting are performed.

