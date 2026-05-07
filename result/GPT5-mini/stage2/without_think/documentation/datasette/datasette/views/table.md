# `table.py`

## `datasette.views.table.Row` · *class*

## Summary:
Represents a single table row as a small, iterable wrapper around a list of "cell" dictionaries; provides convenient access to raw and display values by column name and a JSON-friendly string representation.

## Description:
Row is instantiated when higher-level table rendering or row-processing code needs a lightweight object to represent one result row. It exists to:
- Provide iteration over the underlying cells.
- Allow dictionary-like access to the raw cell value by column name (row["column_name"]).
- Provide access to the cell's rendered/display value (row.display("column_name")).
- Provide a compact JSON string representation that omits special-link columns.

Callers/Factories:
- Typically constructed by table view or row-building code that converts a database result row into a list of cell dictionaries. In this repository, it is used in the context of datasette view rendering code in the same module (datasette.views.table) to pass row data to templates and utilities.

Responsibility boundary:
- Row is strictly a presentation-layer wrapper around an ordered collection of cell dictionaries. It does not query databases, mutate cells, or validate types beyond using the structures provided. It assumes its caller supplies properly-formed cell dictionaries.

## State:
Attributes (public):
- cells : list[dict]
    - Description: The ordered list of cell dictionaries that back this Row.
    - Required keys per cell dict:
        - "column" (str): column name/key used for lookup.
        - "raw" (any): underlying raw value (used by __getitem__ and __str__).
        - "value" (any): display value (used by display()).
        - Optional key:
            - "is_special_link_column" (truthy/falsy): when truthy, that cell is treated as a special link and is omitted from the __str__ JSON output.
    - Constraints: cells must be an iterable (typically list). Each element should be a mapping with at least the "column" key; otherwise runtime KeyError will occur when code assumes "column" exists.
Class invariants:
- self.cells is an iterable of mappings where each mapping includes a "column" key.
- Column names are expected to be unique within self.cells (the implementation returns the first matching cell for a column). Uniqueness is not enforced but recommended by callers.

## Lifecycle:
Creation:
- Instantiate with Row(cells), where cells is an iterable (usually a list) of cell dictionaries as described above.
Usage:
- Typical sequence:
    1. Create Row instance with a prepared cells list.
    2. Templates or view logic iterate over row (for cell in row) to render columns in order.
    3. Access raw values via indexing: value = row["column_name"].
    4. Access display/rendered values via: display_value = row.display("column_name").
    5. Optionally obtain a compact JSON string via str(row) (useful for debug/logging).
- Methods can be called in any order after construction; there is no required complex sequencing between calls.
Destruction:
- No explicit cleanup required. Row holds only references to the provided cell dictionaries and does not manage external resources.

## Method Map:
Mermaid diagram showing typical call relationships and invocation order:

graph LR
    A[Row.__init__] --> B[Row.__iter__]
    A --> C[Row.__getitem__]
    A --> D[Row.display]
    A --> E[Row.__str__]
    E --> C

(Explanation: __str__ depends on __getitem__ to compose its JSON mapping. __iter__, __getitem__, and display are independent operations typically used by template or rendering code.)

## Methods (behavioral details):
- __init__(cells)
    - Inputs: cells (iterable)
    - Behavior: stores the provided iterable on self.cells. No validation is performed beyond assignment.
    - Edge cases: If cells is not iterable, Python will raise a TypeError when callers try to iterate or when methods access cells.
- __iter__():
    - Returns: iterator over self.cells (yields each cell dict in order).
    - Behavior: allows "for cell in row" usage. Does not copy cells.
- __getitem__(key):
    - Inputs: key (typically str) representing a column name.
    - Returns: the "raw" value from the first cell dict whose "column" equals key.
    - Behavior: linear search through self.cells; returns cell["raw"] for the first match.
    - Raises: KeyError if no cell with matching "column" is found.
    - Notes: If multiple cells share the same "column" name, the first match is returned — callers should avoid duplicate column names.
- display(key):
    - Inputs: key (typically str) representing a column name.
    - Returns: the "value" (display/rendered) of the first matching cell, or None if no matching cell is found.
    - Behavior: linear search through self.cells; returns cell["value"] for the first match, otherwise None.
- __str__():
    - Returns: a pretty-printed JSON string (indent=2) representing a mapping of column -> raw value for every cell that does not have truthy "is_special_link_column".
    - Implementation detail: collects columns from self.cells excluding those with is_special_link_column truthy, then uses __getitem__ to fetch the raw value for each included column, and json.dumps(..., default=repr, indent=2) to serialize. Using default=repr makes the output resilient to non-JSON-serializable values (they will be represented by their repr string).
    - Edge cases: Because __str__ builds its column list from the same cells it then indexes, no KeyError should occur in normal, well-formed cell lists.

## Raises:
- KeyError from __getitem__(key) when there is no cell whose "column" equals key.
- Runtime exceptions that may arise from malformed cells:
    - KeyError if a cell dict lacks the "column" key (for any code that expects it).
    - TypeError if cells is not iterable when callers attempt iteration.
- __init__ performs no explicit validation and does not raise on its own.

## Example:
Given a well-formed cells list:

cells = [
    {"column": "id", "raw": 42, "value": "42"},
    {"column": "name", "raw": "Alice", "value": "Alice"},
    {"column": "profile_link", "raw": "/users/42", "value": "<a ...>", "is_special_link_column": True}
]
row = Row(cells)

# Iterate cells
for cell in row:
    # cell is each dict in original order
    pass

# Access raw and display values
raw_id = row["id"]            # => 42
display_name = row.display("name")  # => "Alice"

# Missing column
missing = row.display("email")  # => None
# row["email"] would raise KeyError

# String representation (omits special link column)
print(str(row))
# Produces JSON mapping for id and name only (profile_link omitted)

### `datasette.views.table.Row.__init__` · *method*

## Summary:
Initializes the Row instance by storing the sequence of cell dictionaries that represent a single table row; this sets the object's primary state used by iteration, lookups, and display helpers.

## Description:
This constructor accepts a pre-built collection of "cell" mappings and attaches it to the Row instance as its canonical row data. Typical usage is when code that renders or manipulates tabular results assembles a list/sequence of cell dictionaries for a row and wraps them in a Row object so the rest of the view layer can iterate over, index, or obtain display values from the row.

Known callers and lifecycle stage:
- Constructed at the point where query results are transformed into per-row cell dictionaries for rendering or API serialization (i.e., during table view preparation in the same module or calling view code). The module that defines Row prepares and passes these cell dictionaries before rendering or further processing.
- The Row object is short-lived and used immediately after construction for iteration (__iter__), keyed access (__getitem__), display lookups (display), or debugging/serialization (__str__).

Why this is a separate method:
- Encapsulates the row's cell storage behind a distinct object so lookup, iteration, and display logic (implemented on Row) operate on a single, consistent attribute (self.cells). Keeping construction separate keeps callers simple and centralizes future invariants or validations (if added) in one place.

## Args:
    cells (Iterable[Mapping[str, Any]]):
        An iterable (commonly a list or tuple) of mappings/dictionaries, each representing a single cell in the row.
        Each cell mapping is expected to contain at least the following keys:
          - "column" (str): column name / key for the cell.
          - "raw" (Any): the underlying raw value for keyed access.
        The following keys are used by other Row methods when present:
          - "value" (Any): a presentation-ready value used by display().
          - "is_special_link_column" (bool, optional): used to exclude columns in __str__ output.
        Implementations may allow any additional keys; Row methods only rely on the keys listed above.

## Returns:
    None
    (Constructor; no value is returned. The effect is observed via mutated instance state.)

## Raises:
    None directly.
    Note: __init__ does not validate the argument; if `cells` is not an iterable, subsequent operations (e.g., iterating over the Row, or calling __iter__/__getitem__/display) will raise the usual Python errors (TypeError when attempting to iterate a non-iterable, KeyError from __getitem__ if a requested column is absent).

## State Changes:
    Attributes READ:
        None — this constructor does not read any existing instance attributes.
    Attributes WRITTEN:
        self.cells — assigned to the provided iterable of cell mappings.

## Constraints:
    Preconditions:
        - The caller should provide an iterable of mappings where each mapping contains a "column" key (string) and a "raw" key (value). This is required for Row's other methods to behave correctly.
        - If the caller passes a generator or other one-time iterator, consumers that iterate multiple times (or rely on random-access) may encounter unexpected behavior; provide a sequence if repeated access is needed.

    Postconditions:
        - After return, self.cells references the provided iterable.
        - The instance is ready for iteration (via __iter__), keyed access (via __getitem__), and display lookups (via display) as long as the provided iterable and its elements meet the expected structure described above.

## Side Effects:
    - No I/O, no external service calls.
    - The only mutation is storing the reference to the provided `cells` iterable on the instance (self.cells). The constructor does not copy, validate, or otherwise modify the contents of `cells`.

### `datasette.views.table.Row.__iter__` · *method*

## Summary:
Return an iterator over the Row's cell entries so the Row object can be iterated (e.g., in for-loops or converted to list/tuple) without modifying the Row's internal state.

## Description:
This method implements the Python iteration protocol for Row by returning an iterator over the Row.cells collection. Typical callers are any code that expects to iterate Row objects, for example:
- template or view rendering code that loops over a row to render its cells,
- code producing CSV/JSON/other exports that enumerate cells (e.g., list(row) or tuple(row)),
- generic consumers using "for cell in row:".

This logic is provided as a dedicated method to make Row behave like an iterable container of its cell dictionaries while keeping element access semantics (via __getitem__ and display) separate. Implementing __iter__ keeps iteration logic trivial and efficient (delegates to the underlying cells iterable) and allows Python's iteration and collection conversion utilities to operate on Row instances.

## Args:
None

## Returns:
- iterator of dict: An iterator that yields the elements of self.cells in order. Each yielded element is the same object stored in the underlying collection (typically a dict describing a cell).
- Possible iterator types: depends on the type of self.cells; in the common case self.cells is a list and the return value is a list iterator.

Edge cases:
- If self.cells is not set to an iterable (for example, None or a non-iterable object), a TypeError will be raised by the built-in iter() call.

## Raises:
- TypeError: If self.cells is not an iterable (this is raised by iter(self.cells), not by this method explicitly).
- Any exceptions raised by the underlying iterable's iterator (rare; e.g., if self.cells' __iter__ implementation raises).

## State Changes:
Attributes READ:
- self.cells

Attributes WRITTEN:
- None. This method does not modify the Row instance.

## Constraints:
Preconditions:
- self.cells must be present and be an iterable (commonly a list) of cell objects/dictionaries.
- The structure of each cell element is expected by other Row methods; typical cell dictionaries include keys seen elsewhere in the class: "column", "raw", "value", and optionally "is_special_link_column".

Postconditions:
- The Row object remains unchanged after calling __iter__.
- The returned iterator will yield the elements of self.cells in iteration order. Consuming the iterator does not alter self.cells itself (but may affect iterator state); mutating individual yielded cell objects will affect the objects stored in self.cells because the iterator yields references.

## Side Effects:
- No I/O or external service calls.
- No mutation of external objects performed by this method itself. However, because the iterator yields references into the internal collection, consumer code may mutate those objects, which will be reflected in self.cells.

### `datasette.views.table.Row.__getitem__` · *method*

## Summary:
Provides mapping-style access to the raw value for a column in this row by scanning the row's cells and returning the first matching cell's raw value; does not modify object state.

## Description:
This method implements lookup-by-column-name for a Row instance. It iterates over self.cells and returns the "raw" field of the first cell whose "column" equals the supplied key.

Known callers and usage contexts:
- Row.__str__: uses this method to build a dictionary of column -> raw value when converting the row to a JSON string representation. This occurs when the row is being serialized for debugging or display.
- Callers that treat Row like a mapping and need the unformatted/raw stored value for a particular column (e.g., view rendering code, serialization utilities).
Lifecycle stage: invoked when a consumer of a Row needs direct access to the stored raw cell value by column name (typically during rendering/serialization or when transforming a QueryView result row).
Reason for being a separate method: centralizes column-name lookup logic (including the "first match" semantics) so other code (like __str__ and external consumers) can access raw values using simple subscription syntax (row[key]) without duplicating iteration logic.

## Args:
    key (Any): The column identifier to look up. In typical usage this is a string equal to the cell["column"] values. The comparison uses equality (==), so any value that compares equal to a cell's "column" is acceptable.

## Returns:
    Any: The value of cell["raw"] for the first cell whose cell["column"] == key.
    - If the matching cell's raw value is None, None is returned.
    - If multiple cells have the same "column" value, the raw value from the first occurrence in self.cells is returned.

## Raises:
    KeyError: Raised when no cell in self.cells has a "column" equal to key.

## State Changes:
    Attributes READ:
        - self.cells (iterated and read; each element expected to be a mapping with at least "column" and "raw")
    Attributes WRITTEN:
        - None (this method does not modify self or other objects)

## Constraints:
    Preconditions:
        - self.cells must be an iterable (typically a list) of mappings (dict-like) where each mapping contains a "column" key and a "raw" key.
        - Consumers should expect O(n) lookup cost (linear in number of cells), so repeated lookups in hot paths may warrant a different access pattern or a precomputed mapping.
    Postconditions:
        - No mutation of self or its cells.
        - Either returns the first matching raw value or raises KeyError if no match exists.

## Side Effects:
    - None. No I/O, no external calls, and no mutations to objects outside self.

## Notes and usage tips:
    - If you want a non-raising lookup that returns None when the column is missing, use Row.display(key) which returns cell["value"] for a matching column or None when missing (note: display returns the formatted/display value, not "raw").
    - Because lookup is linear, if callers frequently access many columns by name it may be more efficient to convert cells into a dict mapping column->raw once.

### `datasette.views.table.Row.display` · *method*

## Summary:
Return the presentation-ready value for the named column from this Row, or None when no cell matches.

## Description:
Scans the row's internal sequence of cell dictionaries and returns the "value" field from the first cell whose "column" equals the provided key.

Known callers and context:
- There are no callers inside the Row class itself. This method is intended for external consumers (for example, rendering templates, API serializers, or view code) that need the display/prepared value for a column rather than the raw stored value.
- This logic is a small, focused helper to avoid duplicating the cell-lookup-and-selection loop wherever a display value is required.

## Args:
    key (Any): The column identifier to look up. Typical usage is with string column names, but any object comparable with the stored cell["column"] values is accepted.

## Returns:
    Any or None: The value of cell["value"] from the first matching cell (iteration order of self.cells), or None if no cell has cell["column"] == key.
    - The returned value can be any type provided by the code that constructed the cells (string, number, markupsafe.Markup, etc.).

## Raises:
    KeyError:
        - If an iterated cell dictionary does not contain the "column" key, the attempt to access cell["column"] will raise KeyError.
        - If a cell matches the key but does not contain the "value" key, attempting to return cell["value"] will raise KeyError.
    TypeError:
        - If self.cells is not an iterable (e.g., None or a non-iterable object), the for-loop will raise a TypeError.

## State Changes:
    Attributes READ:
        - self.cells: iterated to search for a matching cell.
    Attributes WRITTEN:
        - None. The method does not modify self or any external objects.

## Constraints:
    Preconditions:
        - The Row instance should have been constructed with an iterable of mapping-like cell objects (dictionaries are expected).
        - Each cell is expected to have a "column" key; to reliably return a value, matching cells should include a "value" key.
    Postconditions:
        - The Row instance is unchanged.
        - The method returns the first matching cell["value"] or None when no matching cell exists.

## Side Effects:
    - None. The method performs no I/O and does not call external services or mutate objects outside the Row instance.

## Behavior notes and edge cases:
    - Complexity: O(n) in the number of cells; the loop stops at the first match.
    - First-match semantics: If multiple cells share the same "column" value, only the first encountered cell's "value" is returned.
    - Compare with __getitem__(key): __getitem__ returns cell["raw"] and raises KeyError when no matching cell is found; display(key) returns None when missing and returns cell["value"] (presentation form) when present.

### `datasette.views.table.Row.__str__` · *method*

## Summary:
Returns a pretty-printed JSON string mapping each non-special column name to its raw value for this Row instance.

## Description:
This method produces a stable, human-readable serialization of the row's raw values suitable for debugging, logging, or any context that calls str(row) or otherwise converts a Row to text. It collects column names from the Row.cells sequence, excludes cells flagged as special link columns, looks up each column's raw value via the Row.__getitem__ lookup, and dumps the resulting mapping as indented JSON using repr() as a fallback for non-JSON-serializable objects.

Known callers and context:
- There are no explicit callers referenced here in this file; this method is invoked whenever the Row object is converted to a string (for example, via str(row), print(row), or logging). It is therefore used at presentation or diagnostic stages where a concise textual representation of the row's raw data is helpful.

Why this logic is a separate method:
- Centralizes a consistent, readable textual representation for the Row type (so all consumers get the same formatting).
- Keeps presentation/serialization concerns out of data-access methods like __getitem__ or display().
- Encapsulates exclusion of special link columns in one place so other code need not repeat that logic.

## Args:
- None

## Returns:
- str: A JSON-formatted string (indentation level 2) representing a dict where:
    - keys are column names (strings) taken from the Row.cells entries that are not marked as special link columns,
    - values are the corresponding raw values obtained from Row.__getitem__.
  Example return (when two columns "id" and "name" are present):
  {
    "id": 1,
    "name": "Alice"
  }
  Edge cases:
  - If no non-special columns are present, returns the JSON string "{}" formatted with indentation.
  - Non-JSON-serializable values are converted with repr() before inclusion (json.dumps default=repr).

## Raises:
- No exceptions are explicitly raised by this method in normal operation.
- In pathological cases where Row.cells is mutated between the list-of-keys construction and value lookup, Row.__getitem__ could raise KeyError — this is not expected given typical Row construction where keys are derived from the same cells list.

## State Changes:
- Attributes READ:
    - self.cells (iterated to build the list of column names and accessed indirectly via __getitem__)
- Attributes WRITTEN:
    - None (this method does not mutate self or external state)

## Constraints:
- Preconditions:
    - self.cells must be an iterable (typically a list) of mapping-like objects (dicts) where:
        - each element contains a "column" key with the column name (string),
        - for any column name used, there exists a corresponding element whose "raw" key holds the raw value (so that __getitem__ can return it).
    - Cells that should not be included must be marked by a truthy "is_special_link_column" key (those will be excluded).
- Postconditions:
    - The method returns a string containing the JSON representation described above.
    - No attributes of self or external objects are modified.

## Side Effects:
- None. There is no I/O, no network access, and no mutation of objects outside of the method's local scope.

## `datasette.views.table.TableView` · *class*

*No documentation generated.*

### `datasette.views.table.TableView.sortable_columns_for_table` · *method*

## Summary:
Return a set of column names that should be treated as sortable for a specific table, honoring an explicit "sortable_columns" entry in table metadata and otherwise falling back to inspecting the table's columns; optionally include the SQLite "rowid".

## Description:
This asynchronous helper centralizes the decision of which columns are considered sortable for a given table. It performs two resolution strategies in order:
1. If the table metadata (self.ds.table_metadata(database_name, table_name)) contains a "sortable_columns" entry, that value is used to construct the returned set.
2. Otherwise, it awaits db.table_columns(table_name) to obtain the table's column names and constructs the returned set from that list.

Because it may need to perform asynchronous schema inspection, and because the metadata override is a clearer source of truth, this logic is implemented as a separate async method so callers (other methods in this TableView class or request-handling code that render table pages or build ORDER BY clauses) can reuse the same resolution behavior without duplicating metadata checks or awaiting the schema call inline.

Note: This is an async coroutine and must be awaited by callers.

## Args:
    database_name (str):
        Key used to index self.ds.databases to obtain the database object. Must be present in that mapping; otherwise indexing will raise KeyError.
    table_name (str):
        The table identifier passed to either the metadata lookup and/or db.table_columns.
    use_rowid (bool):
        If True, the returned set will include the string "rowid" in addition to columns discovered via metadata or schema inspection.

## Returns:
    set[str]:
        A set containing column names (strings) considered sortable. Specifics:
        - If table metadata contains "sortable_columns", the method returns set(table_metadata["sortable_columns"]).
        - Otherwise, it returns set(await db.table_columns(table_name)).
        - If use_rowid is True, "rowid" is added to the set before returning.
        - The set may be empty if metadata provides an empty list or the table has no columns.

## Raises:
    KeyError:
        If database_name is not a key in self.ds.databases, accessing self.ds.databases[database_name] raises KeyError.
    TypeError:
        - If table_metadata["sortable_columns"] exists but is None or otherwise non-iterable, calling set(...) on it raises TypeError.
        - If table_metadata is not a mapping-like object supporting "in", the membership test ("sortable_columns" in table_metadata) may raise TypeError.
    Any exception raised by db.table_columns(table_name):
        Errors from the awaited db.table_columns call propagate; this includes database-specific exceptions and may include QueryInterrupted (imported in this module) if the underlying inspection is interrupted.

## State Changes:
    Attributes READ:
        - self.ds
        - self.ds.databases (indexing with database_name)
        - self.ds.table_metadata(database_name, table_name)
        - db (the returned database object) and its table_columns method (awaited)
    Attributes WRITTEN:
        - None. The method does not mutate self or external objects; it only builds and returns a new set.

## Constraints:
    Preconditions:
        - self.ds must be initialized and contain a mapping attribute "databases" that can be indexed by database_name.
        - table_name should be a valid table identifier for the database when db.table_columns is called.
        - Callers must await this coroutine to obtain the resulting set.
    Postconditions:
        - A set is returned containing the resolved sortable column names; if use_rowid was True, "rowid" is guaranteed to be present in the returned set.
        - No side effects on self or the underlying database objects beyond any read-only operations performed by db.table_columns.

## Side Effects:
    - May perform asynchronous I/O: awaiting db.table_columns(table_name) typically executes a database introspection operation.
    - No filesystem or network side effects beyond the database access performed by db.table_columns.
    - Does not mutate input objects or attributes on self; returns a freshly constructed set.

### `datasette.views.table.TableView.expandable_columns` · *method*

## Summary:
Collects the foreign-key metadata for a table and resolves the label column for each referenced table, returning a list of (foreign-key-dict, label-column) pairs. The method reads datasource metadata and does not modify the TableView object's state.

## Description:
This asynchronous helper fetches metadata needed to present expandable related rows for a table:
- It asks the database object for all foreign keys that reference or are defined on the specified table.
- For each foreign key record it requests the label column for the foreign key's referenced table, then pairs the two results.

Known callers and context:
- No direct callers were found in the provided source for this component. Intended usage: called by TableView rendering logic (or other TableView helpers) when constructing UI that shows expandable related/linked rows for a table, i.e., the lifecycle stage where table metadata is gathered prior to rendering a page or building row expansion links.

Why this is a separate method:
- Encapsulates two related asynchronous database metadata queries (foreign keys + label column resolution).
- Keeps database-metadata retrieval logic isolated from template/response rendering, and centralizes asynchronous awaits in a single place so callers can simply await this helper and receive ready-to-use pairs.

## Args:
    database_name (str): Key identifying which database in self.ds.databases to query. Must be present in self.ds.databases mapping.
    table_name (str): Name of the table whose foreign keys should be retrieved.

## Returns:
    list[tuple]:
        A list of tuples (fk, label_column) in the same order as yielded by the database.foreign_keys_for_table awaitable.
        - fk (dict): A mapping representing a single foreign-key record as returned by db.foreign_keys_for_table; this method accesses fk["other_table"], so callers may expect that key to be present.
        - label_column (any): The value returned by db.label_column_for_table(fk["other_table"]). The exact type and semantics of this value depend on the database API; typically it will be a string naming a column, but callers should treat it as "whatever the database API returns".

Edge-case return values:
- If the database has no foreign keys for the table, an empty list is returned.
- The list length equals the number of foreign-key records returned by db.foreign_keys_for_table; elements preserve ordering.

## Raises:
    KeyError:
        - If database_name is not a key in self.ds.databases, the mapping access will raise KeyError.
    KeyError (or TypeError) while accessing fk["other_table"]:
        - If a foreign-key dict returned by db.foreign_keys_for_table does not include "other_table", attempting fk["other_table"] will raise KeyError.
    Any exception raised by the underlying database methods:
        - Exceptions originating from await db.foreign_keys_for_table(...) or await db.label_column_for_table(...) are propagated (e.g., database IO errors, query interruptions). This helper does not catch or convert those exceptions.

## State Changes:
    Attributes READ:
        - self.ds (and specifically self.ds.databases)
        - self.ds.databases[database_name] (bound to local variable db)
    Attributes WRITTEN:
        - None. The method does not modify any attributes on self.

## Constraints:
    Preconditions:
        - self.ds must be defined and expose a mapping attribute databases.
        - database_name must exist in self.ds.databases.
        - table_name should be a valid identifier for the database API; this method does not validate table existence itself (DB methods may raise if table is unknown).
        - Each item yielded by db.foreign_keys_for_table(table_name) is expected to be a mapping containing the key "other_table".

    Postconditions:
        - Returns a list of tuples whose first element is the original foreign-key dicts returned by the database API and whose second element is the corresponding value returned by db.label_column_for_table for that referenced table.
        - No mutation of self or other passed-in objects is performed.

## Side Effects:
    - Performs asynchronous calls to database metadata methods (db.foreign_keys_for_table and db.label_column_for_table). These calls may perform database I/O.
    - Does not perform network I/O beyond what the database API itself may do.
    - No modifications are made to external objects or to the database (read-only metadata queries).
    - Awaits are performed sequentially: the label column for each foreign key is requested one-by-one in the order foreign_keys_for_table returns them (no parallelization inside this method).

### `datasette.views.table.TableView.post` · *method*

## Summary:
Handle HTTP POSTs routed to a table endpoint by resolving the target database and table, ensuring the route corresponds to a canned query, and delegating execution to the shared query handler; does not modify the TableView instance.

## Description:
This asynchronous handler is invoked when an incoming HTTP POST is routed to a table-level URL (request.url_vars must contain "database" and "table"). Typical callers:
- The ASGI routing layer that dispatches POST requests to TableView.post for paths like /{database}/{table} (or equivalent route patterns in the application).
- Any middleware or test harness that simulates/forwards a POST request into the Datasette view pipeline.

Lifecycle/context:
- Called during request handling when the client issues a POST to a table route.
- The method resolves the database by route, decodes the table name, fetches a "canned query" config for the (database, table) and the current actor, asserts that a canned query exists (POSTs are only allowed to canned queries), and forwards execution to QueryView.data to produce the final response.

Why separate:
- The logic focuses on POST-specific validation and delegation for table routes (database/table route resolution and canned-query enforcement). Query execution, response rendering, and permission checks are handled by QueryView.data, so this method exists to enforce the POST-to-canned-query constraint and reuse the existing query execution pipeline.

## Args:
    request (object): ASGI request-like object (must provide):
        - url_vars (dict-like): must contain keys "database" and "table" whose values are URL-escaped strings (tilde-encoded form is expected).
        - actor: the authenticated actor/principal used when resolving canned queries and permission checks.
    There are no defaults.

## Returns:
    Any: The return value is whatever QueryView.data returns. In practice this is an awaitable result representing an HTTP response (e.g., a Response object or ASGI-compatible response body/headers that the application expects). Edge-case return values are those produced by QueryView.data (error pages, redirect responses, or successful query results).

## Raises:
    NotFound: If the database route does not resolve to a known database (self.ds.get_database(route=...) raises KeyError).
    AssertionError: If no canned query is returned for the resolved (database, table) and actor. The code uses an assertion with the message "You may only POST to a canned query".
    Any exception raised by:
        - self.ds.get_canned_query(database_name, table_name, request.actor)
        - QueryView(self.ds).data(...)
    Those exceptions are propagated and include database/query execution errors or permission-related errors raised by the underlying components.

## State Changes:
    Attributes READ:
        - self.ds : Datasette/application object — used to resolve a database and to fetch canned query metadata.
    Attributes WRITTEN:
        - None. This method does not mutate attributes on self.

## Constraints:
    Preconditions:
        - request.url_vars must be present and contain "database" and "table".
        - request.actor must be set (used by get_canned_query for permission checks).
        - self.ds must implement:
            - get_database(route=str) -> database object or raise KeyError
            - get_canned_query(database_name, table_name, actor) -> dict-like canned query or falsy
        - The canned query returned (if any) must include an "sql" key (a SQL string). Optional keys that will be forwarded:
            - "params" (named parameters mapping)
            - "write" (truthy value indicating this canned query performs writes)
    Postconditions:
        - If the call returns successfully, the result produced is the response generated by QueryView.data for the canned query SQL and parameters.
        - The TableView instance and self.ds remain unchanged.

## Side Effects:
    - I/O: Asynchronously calls into application datastore to:
        - look up a database by route (may read configuration),
        - fetch canned-query metadata,
        - execute the canned query via QueryView.data (which may execute SQL and perform database reads or writes).
    - External mutations: If the canned query includes or triggers write operations (canned_query["write"] truthy), QueryView.data may execute mutations in the underlying database; those side effects are produced by QueryView.data, not by this method.
    - Security/permission delegation: This method relies on self.ds.get_canned_query to enforce actor-based permission constraints; it does not perform its own access checks beyond requiring a canned query exist.

## Implementation notes / edges to preserve:
    - The method decodes URL-escaped names using tilde_decode before lookup.
    - It deliberately asserts that POST is only allowed on canned queries; callers should expect an AssertionError when a POST targets a non-canned table route.
    - All exceptions from underlying components are propagated to the caller; calling contexts (framework/middleware) are expected to handle exceptions and convert them into HTTP error responses as appropriate.

### `datasette.views.table.TableView.columns_to_select` · *method*

## Summary:
Compute and return the ordered list of column names to select for a table response by applying and validating "_col" (include) and "_nocol" (exclude) query parameters. This is a pure computation and does not modify object state.

## Description:
Parses, validates, and applies "_col" and "_nocol" request query parameters to derive the final column list used by table view handlers. Centralizing this logic ensures consistent validation, ordering, and deduplication behavior across table-related endpoints.

Known callers and context:
- Used by TableView request handlers during request processing when building the set and order of columns for rendering or exporting table rows (HTML views, JSON/CSV endpoints, etc.).
- Called at the stage when the handler needs the definitive column list before executing queries or formatting output.

Why separate:
- Keeps parameter parsing and validation in one place for maintainability and consistent behavior.
- Makes deduplication, ordering, and error handling easy to test and reuse.

## Args:
    table_columns (Iterable[str]):
        Iterable of all column names defined for the target table. Used as the authoritative set for validating requested columns and for the default column ordering when no "_col" is provided.
    pks (Iterable[str]):
        Sequence of primary-key column names for the table. When "_col" is provided, this exact sequence is prepended to the returned list. NOTE: this method does not verify that pks are members of table_columns.
    request (object):
        Request object whose .args must support:
          - membership testing ("_col" in request.args)
          - getlist(name) -> list[str] for retrieving possibly repeated query parameter values (used for both "_col" and "_nocol").

## Returns:
    list[str]:
        Final ordered list of column names to select, with behavior determined by the presence of query parameters:
        - No parameters: list(table_columns) preserving table_columns' iteration order.
        - "_col" present: returns a list formed by:
            1. Starting with list(pks) (exact order of pks).
            2. Extending with the validated "_col" entries in the order provided, deduplicated among themselves using dict.fromkeys (first occurrence kept).
           Important: deduplication is applied only to the "_col" entries; if a primary-key name appears both in pks and in "_col", the name will appear twice (once from pks, once from the extended deduplicated _col entries).
        - "_nocol" present: after any "_col" processing, validated names from "_nocol" are removed from the current column list (if present).
        Edge cases:
          - Duplicate names in the raw "_col" parameter are removed (first occurrence kept).
          - The returned list may include pk names not present in table_columns because pks are not validated.
          - Removing a name listed in "_nocol" that is not present in the current list has no effect.

## Raises:
    DatasetteError(status=400):
        - If "_col" is present and any value in request.args.getlist("_col") is not found in table_columns.
          Message: "_col={comma-separated-invalid} - invalid columns"
        - If "_nocol" is present and any value in request.args.getlist("_nocol") is invalid because it either does not exist in table_columns or it references a primary-key column (primary keys are forbidden in "_nocol").
          Message: "_nocol={comma-separated-invalid} - invalid columns"
        Validation is performed before modifying the column list; errors are raised immediately with HTTP 400.

## State Changes:
    Attributes READ:
        - None on self.
    Attributes WRITTEN:
        - None on self.

## Constraints:
    Preconditions:
        - table_columns: iterable of strings representing valid table column names.
        - pks: sequence of strings representing primary-key columns (may or may not be members of table_columns; this method does not enforce that).
        - request.args implements membership testing and getlist(name) -> list[str].
    Postconditions:
        - Every non-primary-key name present in the returned list is a member of table_columns (validated).
        - If "_col" was provided, returned list begins with pks in the given order, followed by validated "_col" entries (deduplicated among themselves).
        - If "_nocol" was provided, none of its validated names will appear in the returned list; validated "_nocol" items are those that both exist in table_columns and are not in pks (otherwise an error is raised).

## Side Effects:
    - No I/O or network activity.
    - No mutation of self, request, table_columns, or pks.
    - Raises DatasetteError to signal client errors (HTTP 400) when validation fails.

## Processing order summary:
    1. Start with columns = list(table_columns)
    2. If "_col" present:
         a. columns = list(pks)
         b. validate all requested "_col" entries against table_columns
         c. extend columns with dict.fromkeys(_col_list) (deduplication among _col entries only)
    3. If "_nocol" present:
         a. validate each requested "_nocol" entry is in table_columns and not in pks
         b. remove validated "_nocol" entries from columns
    4. Return columns

## Examples:
    - Default: table_columns=['a','b','c'], pks=['a'], no params -> ['a','b','c']
    - With _col: table_columns=['a','b','c'], pks=['id'], request._col=['b','a'] -> ['id','b','a']
    - Duplicate handling: table_columns=['a','b'], pks=['a'], request._col=['a','b','a'] -> ['a','a','b'] (pk 'a' prepended, _col deduplicated to ['a','b'], resulting in duplicate 'a')
    - _nocol: table_columns=['a','b','c'], pks=['a'], request._nocol=['b'] -> ['a','c']

Notes:
    - The method is async but contains no await expressions; it completes synchronously and is safe to call from async handlers.

### `datasette.views.table.TableView.data` · *method*

## Summary:
Wraps the table data generation routine in a tracing child-task context and returns the result produced by the underlying implementation.

## Description:
This asynchronous method is the public entry point used by the view/router to produce a table response for an incoming request. It creates a tracer child-task context using tracer.trace_child_tasks() and then awaits and returns the result of the internal implementation method (self._data_traced). The wrapper itself performs no business logic — it exists to ensure that all asynchronous work performed while producing the table data is recorded under a tracing span.

Known callers and lifecycle:
- The ASGI routing / view-dispatch layer invokes this method when serving a request for a table page (it is the canonical entry point for producing table data).
- Internally, this is the immediate caller of self._data_traced; _data_traced performs the actual data lookup, filtering, pagination, facets, and template-context construction.

Why this logic is factored out:
- Tracing concerns are orthogonal to the data-production logic. Placing the tracing context in this thin wrapper keeps the implementation of the core behavior (_data_traced) free of tracing instrumentation and keeps the public entry point small and clearly responsible for instrumentation.

## Args:
    request (object):
        ASGI request-like object. Must provide:
            - url_vars (mapping): contains "database" and "table".
            - args (MultiDict-like): query parameters with get(), getlist(), and iteration.
            - actor (object): used for permission checks.
    default_labels (bool, optional):
        Fallback used when request.args._labels is absent or invalid. Defaults to False.
    _next (str|None, optional):
        Optional pagination cursor passed programmatically; if provided it takes precedence over request.args["_next"].
    _size (int|str|None, optional):
        Optional page size passed programmatically; if provided it takes precedence over request.args["_size"]. Allowed special value: "max".

## Returns:
    The exact return value is whatever self._data_traced returns. In normal operation this is an awaitable that resolves to a 3-tuple:
        (context_dict, extra_template_async_callable, (preferred_template, fallback_template))
    where context_dict contains the table view context (database, table, rows, paging info, facets, etc.), extra_template_async_callable is an async zero-argument function that produces further template context when invoked, and the templates tuple contains preferred and fallback template names.

    Edge-case / delegated returns:
    - If a canned query is configured for the requested table, the wrapper returns the result delegated from QueryView.data (whatever that returns).
    - If a redirect is required (e.g., deprecated query parameters), the underlying implementation may return a redirect ASGI response object instead of the 3-tuple.

## Raises:
    This wrapper does not itself perform validation or DB access, but will propagate exceptions raised by self._data_traced and the operations it calls. Common exceptions that can be raised (by the underlying implementation) include:
    - NotFound: when the database route is not found or the table/view does not exist.
    - Forbidden: if the requesting actor lacks permission to view the table.
    - DatasetteError: for invalid combinations or values of sorting/filter arguments (e.g., both _sort and _sort_desc provided, or non-sortable column specified).
    - BadRequest: for invalid _size values, disallowed facet usage, or invalid _col/_nocol parameters.
    - Database-related exceptions raised by db.execute or other DB helpers.
    Note: QueryInterrupted is handled by the underlying implementation in specific places (e.g., count query) and is not re-raised by this wrapper.

## State Changes:
Attributes READ:
    - self._data_traced: called to perform all table data generation work.
    - tracer (module-level): trace_child_tasks() context manager is used.

Attributes WRITTEN:
    - None. This wrapper does not mutate attributes on self.

## Constraints:
Preconditions:
    - request.url_vars must include "database" and "table".
    - self._data_traced must be implemented and async-callable on the TableView instance.
    - The Datasette instance (self.ds) and related helpers expected by _data_traced must be properly configured (databases, settings, plugin manager, etc.).

Postconditions:
    - The method returns exactly what self._data_traced returns (the 3-tuple context or a delegated/redirect response).
    - No mutation of the TableView instance state is performed by this wrapper.

## Side Effects:
    - Enters a tracer.child_tasks context (instrumentation effect) for distributed tracing; this affects tracing output but does not change application state.
    - All I/O, DB queries, plugin calls, and potential redirects are performed by self._data_traced — this wrapper causes those side effects only by invoking that method.

### `datasette.views.table.TableView._data_traced` · *method*

## Summary:
Builds and returns the data context, an asynchronous extra-template provider, and template names for rendering a table view — applying request filters, sorting/pagination, facets, column expansion, and access checks without mutating the TableView instance.

## Description:
This asynchronous method performs the end-to-end work required to produce the data context for a table page. It is invoked after top-level instrumentation (TableView.data wraps this method inside tracer.trace_child_tasks()). The method:

- Resolves the requested database and table from request.url_vars and obtains a database handle.
- Checks for and delegates to a "canned query" (predefined query) if configured for the table.
- Verifies the table exists and the requesting actor has visibility permissions.
- Normalizes and validates request arguments used for redirecting deprecated parameters.
- Determines primary keys, columns to select, and whether rowid should be used.
- Builds Filters from request.args, produces WHERE clauses and SQL parameters, and applies plugin-provided filter hooks.
- Determines sortable columns and validates _sort/_sort_desc values and combinations.
- Constructs SQL fragments (from_sql, count_sql, final select SQL with optional ORDER/LIMIT/OFFSET).
- Handles pagination via _next, translating next cursors into additional WHERE clauses or offsets and computing next links.
- Executes the data query and (unless suppressed) a count query to determine filtered row count. Query timeouts are handled via QueryInterrupted.
- Invokes plugin hooks to register facet classes, executes facet computations in parallel (unless disabled) and suggested facets.
- Extracts result column names and rows; optionally expands foreign-key label columns via Datasette expansion helpers and replaces row values with CustomRow objects containing {"value","label"} pairs.
- Computes the next cursor and next_url if there are more rows than the page size.
- Builds a human-readable description for the applied filters and sort.
- Produces an extra_template callable (async function) which assembles display_columns/display_rows, table actions, metadata, and other view-specific rendering context when invoked by a renderer.
- Returns a 3-tuple: (context dict, extra_template async callable, (preferred_template, fallback_template)).

This logic is split into its own method to separate the traced, instrumented work (wrapped by TableView.data) from external tracing concerns and to keep the high-level request entry point small.

Known callers:
- TableView.data — calls this method while creating child tracing spans; this is the canonical entry point for producing a table response context.

## Args:
    request (object): ASGI request-like object with:
        - url_vars (mapping): contains "database" and "table" route variables (URL-encoded / tilde-encoded).
        - args (MultiDict-like): query parameters; supports get(), getlist(), and iteration.
        - actor (object): actor performing the request (used for permission checks).
      Required: request.url_vars["database"] and request.url_vars["table"] must exist.
    default_labels (bool, optional): Fallback boolean used when _labels query argument is invalid or absent. Defaults to False.
    _next (str|None, optional): Optional pagination cursor passed in programmatically (takes precedence over request.args["_next"]).
    _size (int|str|None, optional): Optional page size passed in programmatically (takes precedence over request.args["_size"]). Allowed special value: "max".

## Returns:
    tuple:
        - context (dict): A mapping containing keys:
            - database (str): resolved database name
            - table (str): resolved table name
            - is_view (bool): True if the named table is a view
            - human_description_en (str): human-readable description of filters/sorting
            - rows (list): page_size-limited list of rows (CustomRow or DB row mappings)
            - truncated (bool): whether the DB result was truncated (results.truncated)
            - filtered_table_rows_count (int|None): approximate filtered row count if available
            - expanded_columns (list[str]): columns whose values were expanded to include labels
            - expandable_columns (list[(fk, label_column)]): available foreign-key expansions
            - columns (list[str]): names of returned columns
            - primary_keys (list[str]): primary key column names (may be empty)
            - units (dict): units metadata for columns
            - query (dict): {"sql": <final SQL string>, "params": <params dict>}
            - facet_results (dict): facet information gathered from plugin facet classes
            - suggested_facets (list): suggested facet metadata
            - next (str|None): opaque next cursor (string) or None
            - next_url (str|None): absolute URL for the next page or None
            - private (bool): whether the table is private as returned by visibility check
            - allow_execute_sql (bool): whether the requesting actor is allowed to execute SQL on the database
        - extra_template (async callable): an async zero-argument function that returns a dict of values used by the template renderer (display_columns, display_rows, table actions, metadata, etc.). When called it may perform additional async DB and plugin calls.
        - templates (tuple[str,str]): (preferred_template_name, fallback_template_name) for rendering (e.g. ("table-{db}-{table}.html", "table.html")).

    Edge-case returns:
        - If a canned_query exists for the table, returns whatever QueryView.data returns (delegated).
        - If a redirect is necessary (deprecated params), the method returns the result of self.redirect(...) which is typically an ASGI response object instead of the described 3-tuple.

## Raises:
    NotFound:
        - If the database route does not correspond to a configured database.
        - If neither a view nor a table exists with the requested name.
    Forbidden:
        - If visibility checks deny the actor access to the table (visible is False).
    DatasetteError:
        - If both _sort and _sort_desc are provided (cannot be used together).
        - If _sort or _sort_desc specify a non-sortable column.
    BadRequest:
        - If _size is provided but is not a positive integer or equals a negative value.
        - If _size exceeds self.ds.max_returned_rows.
        - If _facet parameters are present while dataset setting "allow_facet" is False.
    Any exception raised by underlying components:
        - Database execution (db.execute) may raise database-specific exceptions (propagated).
        - Plugin hooks called via await_me_maybe may raise exceptions — these propagate unless plugin code isolates them.
    Notes:
        - QueryInterrupted while running the count query is caught and treated as a missing count (no exception re-raised).
        - Invalid column names passed via _col / _nocol are handled earlier by columns_to_select which raises DatasetteError.

## State Changes:
    Attributes READ:
        - self.ds (Datasette instance): accessed extensively for databases, settings, URLs, metadata, canned queries, permissions, expansion helpers, configured page sizes and limits, and other utilities.
        - self.columns_to_select (method): called to compute columns to include.
        - self.sortable_columns_for_table (method): called to compute allowed sortable columns.
        - self.expandable_columns (method): called to determine foreign-key columns that can be expanded.
        - self.redirect (method): used to generate redirect responses for deprecated query parameters.
    Attributes WRITTEN:
        - None — this method does not modify attributes on self.

## Constraints:
    Preconditions:
        - request.url_vars must contain "database" and "table" with tilde-encoded values.
        - request.args must implement get(), getlist(), iteration and be stable for multiple reads.
        - self.ds must expose:
            - get_database(route) -> database object with methods: get_view_definition, table_exists, primary_keys, table_columns, table_definition, get_view_definition, table_columns, execute, foreign_keys_for_table, label_column_for_table
            - table_metadata(database, table)
            - get_canned_query(database, table, actor)
            - setting(name) and page_size/max_returned_rows attributes
            - expand_foreign_keys(database, table, column, list_of_values)
            - metadata(), update_with_inherited_metadata, urls.path, absolute_url, inspect_data (optional)
            - permission_allowed(actor, permission, database_name, default=True)
        - Plugin manager pm should implement hook methods used: filters_from_request, register_facet_classes, table_actions.
    Postconditions:
        - Returns the 3-tuple described above (context, extra_template, templates) unless a redirect or canned_query delegation occurs.
        - Does not mutate TableView instance state.
        - The returned context 'rows' list is truncated to page_size (or page_size + 1 is used internally to detect "next"); truncated flag in context reflects underlying result.truncated.
        - SQL and params in context["query"] correspond to the final SELECT that was executed (including any WHERE and ORDER BY applied).

## Side Effects:
    - I/O: performs SQL queries via db.execute (data query and optionally count and prefix lookup queries) — these are blocking async DB I/O.
    - Plugin calls: awaits plugin hooks (filters_from_request, facet classes' facet_results and suggest methods, table_actions) which may perform arbitrary I/O or computations.
    - May call self.redirect(...) which produces a redirect response (I/O effect from ASGI response generation).
    - Calls self.ds.expand_foreign_keys which may execute extra database queries to resolve labels.
    - Calls self.ds.update_with_inherited_metadata (modifies datasette metadata state) during extra_template execution.
    - Calls self.ds.permission_allowed (may check external authentication/authorization backends).
    - No direct filesystem I/O performed by this method itself.

## `datasette.views.table._sql_params_pks` · *function*

## Summary:
Constructs a SELECT SQL string, a parameter dictionary, and the list of primary key column names for querying a single row from a table given primary key values. If the table has no declared primary keys, it falls back to using the SQLite internal rowid.

## Description:
This is a small, reusable helper that builds the SQL WHERE clause and corresponding bound parameters needed to fetch a single row (or rows in the case of compound keys) from a table by its primary key(s). Typical callers are table-row handlers or other view-layer code that must fetch a specific record by primary key and need a safe, parameterized SQL statement to execute against the database. It is separated out so logic for:
- querying the database for declared primary key column names,
- falling back to rowid when no primary keys exist, and
- producing consistent parameter names and ordering
is centralized and not duplicated across multiple view functions.

Known callers / call contexts:
- View-level code that needs to build the SQL and params to fetch a single row from a table by primary key(s). (In this repository this helper is used wherever the code needs a standardized SQL+params representation for a row lookup in datasette.views.table.)

Why this is a separate function:
- Encapsulates database schema inspection (async primary_keys call) and consistent parameter naming/ordering rules.
- Ensures the same escaping and fallback-to-rowid behavior is used everywhere row lookups are needed.
- Keeps view code focused on request/response logic instead of SQL construction details.

## Args:
- db (object, required)
    - An asynchronous database wrapper / connection object that exposes an awaitable method primary_keys(table: str) -> list[str].
    - The function will await db.primary_keys(table) to determine declared primary key column names.
    - The db object may perform I/O when primary_keys is awaited.
- table (str, required)
    - The table name (identifier) in the database to query.
    - This name is passed to escape_sqlite before being inserted into the SQL string; it should be a valid table identifier for the target SQLite database.
- pk_values (iterable of values, required)
    - An iterable (list/tuple/etc.) of primary key values supplied in the same order as the database reports primary key columns from db.primary_keys(table).
    - Each value may be any object acceptable as a bound parameter for the database driver (e.g., int, str, None, bytes).
    - Interdependencies:
        - The expected relationship is len(pk_values) == len(pks) where pks is the list returned by db.primary_keys(table) (or ['rowid'] when the table has no declared primary keys).
        - The function makes no internal assertion: it will create parameters for every item in pk_values, and the SQL WHERE clause is built from pks. If fewer pk_values are supplied than pks, execution of the returned SQL will fail later due to missing bound parameters. If more pk_values are supplied than pks, the extra values will be included in the returned params dict but not referenced by the SQL.

## Returns:
A 3-tuple: (sql, params, pks)
- sql (str)
    - A parameterized SELECT statement of the form:
      select <select_columns> from <escaped_table> where "<pk0>"=:p0 AND "<pk1>"=:p1 ...
    - <select_columns> is "*" when the table has declared primary keys, or "rowid, *" when falling back to rowid.
    - Identifiers (table and column names) are escaped via escape_sqlite(table) and double-quoted column names.
    - The WHERE clause has one equality check per primary key column in pks, in the same order as pks.
- params (dict[str, any])
    - A mapping of parameter names to values suitable for DB parameter binding.
    - Keys are of the form "p0", "p1", ... (matching the :p0, :p1 placeholders used in sql).
    - Built from the supplied pk_values by enumerating them in order. Note: params will contain entries for every pk_value provided; the SQL uses only those parameters whose keys appear in the WHERE clause.
- pks (list[str])
    - The list of primary key column names used to build the WHERE clause.
    - If db.primary_keys(table) returns an empty list (no declared PKs), pks will be set to ["rowid"] and SQL will select "rowid, *".

Possible return examples:
- Table with declared single primary key "id": returns ("select * from \"table\" where \"id\"=:p0", {"p0": value}, ["id"])
- Table with declared composite keys ["a","b"]: returns ("select * from \"table\" where \"a\"=:p0 AND \"b\"=:p1", {"p0": v0, "p1": v1}, ["a","b"])
- Table with no declared primary keys: returns ("select rowid, * from \"table\" where \"rowid\"=:p0", {"p0": value}, ["rowid"])

## Raises:
- Any exception raised by await db.primary_keys(table) propagates out (for example, database connection errors).
- No explicit exceptions are raised by this function for argument validation; incorrect caller-supplied pk_values length will result in later failures when the SQL is executed (missing bound parameters) rather than an immediate exception here.

## Constraints:
Preconditions:
- db must implement an awaitable primary_keys(table: str) -> list[str] method.
- table must be a valid identifier for the target SQLite database (escape_sqlite will be used, but malformed input may still lead to runtime errors).
- The caller should ensure pk_values are provided in the same order as primary key columns returned by db.primary_keys(table) (or provide a single value when using rowid).

Postconditions:
- Returns a syntactically valid parameterized SQL SELECT string and a params dict whose keys are "p0", "p1", ... assigned from pk_values in order.
- pks reflects the column identifiers that appear in the WHERE clause (or ["rowid"] if fallback used).

## Side Effects:
- Awaits db.primary_keys(table): this is an external I/O-like call into the database layer and may perform a query to inspect table schema.
- No file, network, stdout I/O or global state is modified by this function itself beyond the awaited primary_keys call.
- No mutation of caller-provided arguments is performed.

## Control Flow:
flowchart TD
    A[Start: call _sql_params_pks(db, table, pk_values)] --> B[Await db.primary_keys(table)]
    B --> C{Are primary keys returned?}
    C -- Yes --> D[select="*"; pks = primary keys]
    C -- No --> E[select="rowid, *"; pks=["rowid"]]
    D --> F[Build WHERE clauses: one per pk -> '"pk"=:p{i}']
    E --> F
    F --> G[Compose SQL: select <select> from <escaped table> where <joined wheres>]
    G --> H[Enumerate pk_values and populate params p0,p1,...]
    H --> I[Return (sql, params, pks)]

## Examples:
Example 1 — typical single-PK table
- Context: The table "users" has a declared primary key column ["id"].
- Call: supply pk_values containing the id value in the same order as returned by db.primary_keys("users").
- Result: sql is "select * from <escaped users> where \"id\"=:p0", params is {"p0": <id_value>}, pks is ["id"].
- Note: The caller should execute the returned SQL with params using their database execution API.

Example 2 — composite primary key
- Context: The table "orders" has declared primary keys ["user_id", "order_id"].
- Call: supply pk_values [user_id_value, order_id_value] in that order.
- Result: sql has two WHERE comparisons joined with AND: "\"user_id\"=:p0 AND \"order_id\"=:p1"; params contains {"p0": user_id_value, "p1": order_id_value}.

Example 3 — table with no declared PK (rowid fallback)
- Context: The table "logs" has no declared primary key.
- Behavior: function falls back to rowid and sets select to "rowid, *", pks to ["rowid"], and builds WHERE for rowid.
- Caller must pass a single pk_values element giving the rowid to identify the row.

Example 4 — mismatched pk_values length (caller responsibility)
- If the caller provides fewer pk_values than there are columns in pks, the returned SQL will contain placeholders (e.g., :p1) that are not present in params; executing that SQL will raise a database error due to missing parameters.
- If the caller provides more pk_values than pks, the extra values will appear in the returned params dict but will not be referenced by the SQL; this is harmless for execution but indicates a likely caller bug.

Notes for implementers:
- Keep the same parameter naming convention ("p0", "p1", ...) to match other code which expects these placeholder names.
- Ensure escape_sqlite is used to protect the table identifier when composing the SQL.

## `datasette.views.table.display_columns_and_rows` · *function*

*No documentation generated.*

