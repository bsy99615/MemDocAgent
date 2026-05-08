# `csvsql.py`

## `csvkit.utilities.csvsql.CSVSQL` · *class*

*No documentation generated.*

### `csvkit.utilities.csvsql.CSVSQL.add_arguments` · *method*

## Summary:
Adds the csvsql-specific command-line options to the utility's argument parser, mutating self.argparser so the CLI accepts the flags and parameters required by CSV-to-SQL operations.

## Description:
This method registers all command-line arguments used by the csvsql utility (input file paths, SQL dialect selection, database connection options, query/insert options, table naming, inference/sniffing controls, etc.). It is intended to be invoked as part of the CLI initialization phase — i.e., before argument parsing — so that the resulting ArgumentParser contains the expected options.

Known callers and lifecycle context:
- Typically invoked by the CSVKitUtility CLI setup flow when a csvsql command-line utility instance is prepared (for example, during CSVKitUtility.main() or CSVKitUtility.run() before calling parse_args()). The method exists to separate CLI argument registration from parsing/execution logic so that argument definitions are centralized and reusable across test harnesses and runtime.

Why this is a separate method:
- Centralizes and documents all CLI options for csvsql in one place.
- Keeps argument registration decoupled from runtime behavior (parsing, validation, execution), making unit testing and extension easier.

## Args:
This method takes no parameters other than self.

However, it registers the following arguments on self.argparser (each entry lists the flag(s), dest name, type/action, default value, and a concise description):

- FILE (positional)
  - dest: input_paths
  - type/action: nargs='*' (zero or more positional values)
  - default: ['-']
  - description: CSV file path(s) to operate on. If omitted or if '-' is present, stdin is used.

- -i, --dialect
  - dest: dialect
  - type/action: choice from module-level DIALECTS
  - default: None
  - description: SQL dialect to generate. (Help text states it cannot be used with --db; this is informational only.)

- --db
  - dest: connection_string
  - type/action: string
  - default: None
  - description: SQLAlchemy connection string; when provided, generated SQL may be executed directly against this database.

- --query
  - dest: queries
  - type/action: action='append' (may be specified multiple times)
  - default: None (becomes a list if provided)
  - description: Execute one or more SQL queries delimited by ";" and output the result of the last query as CSV. QUERY may be a filename.

- --insert
  - dest: insert
  - type/action: action='store_true'
  - default: False
  - description: Insert the data into the table. Help text indicates Requires --db.

- --prefix
  - dest: (no explicit dest given; add_argument stores into 'prefix' by flag name)
  - type/action: action='append'
  - default: []
  - description: Add an expression following the INSERT keyword (e.g., OR IGNORE or OR REPLACE). Can be specified multiple times.

- --before-insert
  - dest: before_insert
  - type/action: string
  - default: None
  - description: SQL to execute before the INSERT command. Help notes Requires --insert.

- --after-insert
  - dest: after_insert
  - type/action: string
  - default: None
  - description: SQL to execute after the INSERT command. Help notes Requires --insert.

- --tables
  - dest: table_names
  - type/action: string
  - default: None
  - description: Comma-separated list of table names to be created. Default naming uses filenames (without extension) or "stdin".

- --no-constraints
  - dest: no_constraints
  - type/action: action='store_true'
  - default: False
  - description: Generate schema without length limits or null checks.

- --unique-constraint
  - dest: unique_constraint
  - type/action: string
  - default: None
  - description: Column-separated list of column names to include in a UNIQUE constraint.

- --no-create
  - dest: no_create
  - type/action: action='store_true'
  - default: False
  - description: Skip creating the table. Help notes Requires --insert.

- --create-if-not-exists
  - dest: create_if_not_exists
  - type/action: action='store_true'
  - default: False
  - description: Create the table if it does not exist; otherwise continue. Help notes Requires --insert.

- --overwrite
  - dest: overwrite
  - type/action: action='store_true'
  - default: False
  - description: Drop the table if it already exists. Help notes Requires --insert and Cannot be used with --no-create (informational only).

- --db-schema
  - dest: db_schema
  - type/action: string
  - default: None
  - description: Optional database schema name in which to create table(s).

- -y, --snifflimit
  - dest: sniff_limit
  - type/action: int
  - default: 1024
  - description: Limit CSV dialect sniffing to the specified number of bytes. "0" disables sniffing; "-1" sniff the entire file.

- -I, --no-inference
  - dest: no_inference
  - type/action: action='store_true'
  - default: False
  - description: Disable type inference when parsing input.

- --chunk-size
  - dest: chunk_size
  - type/action: int
  - default: None
  - description: Chunk size for batch inserts. Help notes Requires --insert.

## Returns:
- None. The method mutates self.argparser in-place and does not return a value.

## Raises:
- No explicit exceptions are raised by this method.
- Possible runtime errors:
  - AttributeError if self.argparser is not set or does not implement add_argument.
  - Any exceptions raised by the underlying argument parser's add_argument (e.g., duplicate option strings or invalid parameters) will propagate.

## State Changes:
- Attributes READ:
  - self.argparser (reads the attribute to call add_argument)
  - module-level DIALECTS (read when registering choices for the dialect argument)

- Attributes WRITTEN / Mutated:
  - self.argparser (mutated: new argument specifications are added to the parser's internal structures)

## Constraints:
- Preconditions:
  - self must have an attribute argparser, and argparser must support the add_argument(name_or_flags, ...) API (compatible with argparse.ArgumentParser).
  - The module-level name DIALECTS must be defined (used as choices for the dialect argument).

- Postconditions:
  - After calling this method, self.argparser contains the complete set of csvsql CLI options listed above. Calling parse_args() on this parser will populate Namespace attributes with the dest names listed in Args.

## Side Effects:
- No file I/O, network, or database operations are performed.
- The only side effect is mutation of self.argparser (registration of argument handlers), which can affect subsequent argument parsing in the process.

### `csvkit.utilities.csvsql.CSVSQL.main` · *method*

*No documentation generated.*

### `csvkit.utilities.csvsql.CSVSQL._failsafe_main` · *method*

## Summary:
Processes each input file by determining a table name, parsing the CSV into an agate.Table, and either inserting that table into the configured database connection (with optional pre/post SQL hooks and a final transaction commit) or writing a CREATE TABLE statement to the configured output. It mutates the list of pending table names and produces database or output_file side effects.

## Description:
This is the main per-file processing loop invoked during the CSVSQL utility's execution phase (after setup and argument parsing). Typical caller:
- The CSVSQL CLI runner or CSVSQL.run which prepares self.connection, self.input_files, self.table_names, self.args, and other resources and then calls this method to perform import/export.

Why a dedicated method:
- The routine coordinates multiple responsibilities (table-name selection, CSV parsing, conditional DB insertion vs DDL emission, pre/post insertion SQL hooks, queries execution, and transaction commit). Encapsulating it keeps orchestration code separate from IO/DB logic and makes testing and maintenance easier.

## Args:
This method is an instance method and takes no explicit parameters. Instead it reads configuration and state from self. The following attributes on self must exist and are referenced:

- self.connection: SQLAlchemy Connection-like object or None. If truthy:
    - .begin() is called to obtain a transaction object with .commit().
    - .exec_driver_sql(sql) is used to execute ad-hoc SQL statements.
- self.input_files: iterable/list of readable file-like objects (each should be consumable by agate.Table.from_csv). Non-stdin files should provide a .name attribute used to derive fallback table names.
- self.table_names: list[str]. Consumed in order via pop(0) — this list is mutated by the method.
- self.args: object/namespace with attributes:
    - sniff_limit (int): -1 indicates no limit; other ints passed through as sniff_limit to agate.Table.from_csv.
    - skip_lines (int): forwarded to agate.Table.from_csv.
    - before_insert (str or None): semicolon-separated SQL to exec before inserting each table (executed as-is, split on ';' without stripping).
    - after_insert (str or None): semicolon-separated SQL to exec after inserting each table (executed as-is).
    - overwrite (bool): passed to table.to_sql.
    - no_create (bool): create flag passed to to_sql is not no_create.
    - create_if_not_exists (bool): passed to table.to_sql.
    - insert (bool): insertion occurs only if True and the table has rows (len(table.rows) > 0).
    - prefix (str or list): prefixes forwarded to table.to_sql.
    - db_schema (str or None): schema name forwarded to to_sql/to_sql_create_statement.
    - no_constraints (bool): constraints argument passed as not no_constraints.
    - chunk_size (int or None): passed to table.to_sql.
    - dialect (str or dialect object): forwarded to table.to_sql_create_statement when emitting DDL.
    - queries (iterable[str] or None): each entry is either a SQL string or a filesystem path; file contents will be read if a path exists.
- self.reader_kwargs: dict passed as extra keyword args to agate.Table.from_csv.
- self.writer_kwargs: dict passed to agate.csv.writer for query-result CSV output.
- self.output_file: writable file-like object used to emit CREATE statements or CSV result rows.
- self.unique_constraint: value passed to table.to_sql and to_sql_create_statement.
- self.get_column_types(): callable returning column type mapping for agate.Table.from_csv.

## Returns:
- None. The method's effects are side-effecting (database changes, output writes); it does not return a value.

## Raises:
The method does not explicitly raise its own exceptions but will propagate exceptions from its dependencies. Documented propagated conditions:
- agate.Table.from_csv may raise various exceptions — StopIteration is explicitly caught and causes the current input file to be skipped; any other exception from agate (parsing errors, I/O errors) will propagate.
- Database driver exceptions from self.connection.exec_driver_sql or table.to_sql may propagate.
- File I/O errors (e.g., OSError) from opening query files will propagate.
- Important edge-case: if self.args.queries is provided but none of the executed statements returned a non-None "rows" object (i.e., rows remains None), the subsequent access to rows.returns_rows will raise AttributeError. This method does not guard against that; callers should ensure at least one executed query returns rows if they expect CSV output.

## State Changes:
Attributes READ:
- self.connection
- self.input_files
- self.table_names
- self.args and the specific subfields listed above
- self.reader_kwargs
- self.writer_kwargs
- self.output_file
- self.unique_constraint
- the return value of self.get_column_types()

Attributes WRITTEN / Mutated:
- self.table_names: mutated by pop(0) for each input file when an entry exists (pop happens before CSV parsing).
- No other self.* attributes are assigned within the method.

External side-effected state:
- Database schema/data via table.to_sql and exec_driver_sql when self.connection is present.
- Filesystem reads when opening query files referenced in self.args.queries.
- Writes to self.output_file (CREATE statements or CSV rows).
- Underlying DB drivers may perform network or additional I/O.

## Constraints:
Preconditions:
- self.input_files must yield readable file-like objects; non-stdin inputs should expose a .name attribute for fallback naming.
- self.table_names must be a list (possibly empty); pop(0) is attempted once per input file before parsing.
- self.get_column_types() must be callable and return a mapping acceptable to agate.Table.from_csv (or None).
- If self.connection is provided it must implement .begin() and .exec_driver_sql(), and the object returned by .begin() must provide .commit().
- self.output_file must be writable if self.connection is None or if queries produce rows (CSV output).

Postconditions:
- For every input file that successfully yields an agate.Table:
    - If self.connection is present:
        - Optional before_insert SQL segments (split on ';' without stripping) are executed in order.
        - table.to_sql(...) is invoked with flags derived from self.args and self.unique_constraint; this may create and/or insert rows depending on flags and table contents.
        - Optional after_insert SQL segments are executed in order.
    - If self.connection is None:
        - A CREATE TABLE statement for the table will be written to self.output_file followed by a newline.
- After all input files and optional queries are processed, if a transaction was begun via self.connection.begin(), transaction.commit() is called. If an exception occurs before commit, commit will not be reached and the exception will propagate (potentially rolling back depending on the transaction context manager used).
- self.table_names will have had up to one element popped per input file processed (pop occurs before parsing; if pop succeeds and parsing raises StopIteration the name has still been removed).

## Side Effects:
- Database: begins a transaction (if connection truthy), executes arbitrary SQL via exec_driver_sql for before_insert/after_insert hooks and for args.queries, uses agatesql Table.to_sql to create/insert tables, and commits the transaction at the end.
- File IO: reads input files via agate.Table.from_csv; opens and reads files listed in args.queries when os.path.exists(query) is True; writes DDL or CSV output to self.output_file.
- Mutation: modifies self.table_names by popping consumed names.
- Potential error conditions due to side effects:
    - Empty segments from before_insert/after_insert (resulting from split(';')) are executed as empty SQL strings — whether this is tolerated or raises an exception depends on the DB driver. The method does not strip these segments before executing.
    - When executing args.queries, empty segments are created and are later filtered by strip() during execution (the code only executes queries that pass query.strip()), but files/strings that produce only empty/whitespace segments will result in rows remaining None, causing an AttributeError when rows.returns_rows is accessed.

## Notes / Behavior details and edge cases:
- Table name selection:
    - The code first attempts to pop the next name from self.table_names via pop(0). If pop raises IndexError (no names left), a fallback name is used: "stdin" for sys.stdin input, otherwise the basename of f.name without extension.
    - Important: because pop(0) is attempted before parsing, if pop succeeds and subsequent CSV parsing raises StopIteration, the popped name is already consumed and will not be available for later files.
- Sniff limit handling:
    - If self.args.sniff_limit == -1, sniff_limit is converted to None and passed to agate.Table.from_csv to indicate "no limit".
- Empty input files:
    - StopIteration raised by agate.Table.from_csv is caught and causes the method to skip further processing of that input file (no writes, no insert).
- Insert gating:
    - table.to_sql is called with insert=self.args.insert and len(table.rows) > 0. This prevents attempting inserts when the table is empty even if insert mode is enabled.
- Query execution:
    - Each entry in self.args.queries is either interpreted as a path (if os.path.exists(entry) is True — the file is opened and read) or as SQL text directly; in either case the text is split on ';' and the resulting segments are appended to queries list.
    - During execution, the code iterates over queries and executes only those where query.strip() is truthy. The local variable rows is updated with the return value of each exec_driver_sql call; only the final non-empty executed statement's return value will be kept in rows.
    - If none of the executed queries return a non-None rows object, rows remains None and accessing rows.returns_rows will raise AttributeError; this is an observable behavior of the implementation and not guarded here.
- The method intentionally performs minimal filtering of SQL segments (split on ';' but only strips when deciding to execute queries after processing files), so callers should ensure their before_insert/after_insert and queries values are well-formed to avoid driver errors.

## `csvkit.utilities.csvsql.launch_new_instance` · *function*

## Summary:
Create a CSV-to-SQL CLI utility instance and hand control to its run lifecycle, acting as a minimal importable bootstrap that starts the CSVSQL command behavior.

## Description:
- Known callers and typical context:
  - No direct internal callers are required or typically present. This function is intended to be used as a module-level entry point for process startup (for example as a console_scripts packaging entry point), by integration tests that run the utility in-process, or by any external runner that wants to invoke the CSVSQL command behavior programmatically.
  - Typical trigger: the packaging/runtime imports the module and calls this function with no arguments at process start to begin argument parsing and CSVSQL execution, or a test/harness calls it to exercise the utility end-to-end.

- Why this logic is extracted into its own function:
  - Provides a stable, importable, and testable entry point that hides the class name and instantiation details from packaging and runner code.
  - Keeps bootstrapping separate from CSVSQL implementation so callers can start the CLI behavior with a single, consistent call.
  - Delegates parsing, I/O, and operational behavior to CSVSQL.run(), keeping this wrapper trivial and predictable.

## Args:
- None.

## Returns:
- None.
  - The function returns implicitly (None) after CSVSQL.run() completes normally.
  - If CSVSQL.run() blocks (for example during interactive operation or long-running processing), launch_new_instance will block until run() returns or raises.
  - If CSVSQL.__init__ or CSVSQL.run() raises an exception (including SystemExit), that exception propagates and the function does not return normally.

## Raises:
- NameError
  - Condition: The CSVSQL symbol is not defined in the module namespace when attempting to instantiate it (calling CSVSQL()).
- Any exception raised by CSVSQL.__init__
  - Condition: the CSVSQL constructor raises during instantiation (for example due to missing dependencies or constructor-time validation); the exception propagates unchanged.
- Any exception raised by CSVSQL.run()
  - Condition: runtime failures during CSVSQL.run() (argument parsing, I/O, SQL execution, explicit exits, etc.). These exceptions propagate unchanged from the run() implementation.

## Constraints:
- Preconditions:
  - The CSVSQL symbol must be defined and constructable in the module namespace.
  - Any runtime context expected by CSVSQL.run() (for example, correctly-populated sys.argv if the run method parses command-line arguments, access to input files or database connection parameters) should be prepared by the caller; this wrapper does not set up CLI arguments or I/O.
- Postconditions:
  - If the function returns normally, CSVSQL.run() has completed its lifecycle and any side effects produced by it (opening/closing files, writing SQL, connecting to databases, printing to stdout/stderr) have already occurred.
  - No value is returned to indicate success; callers must rely on absence of raised exceptions or other externally observable side effects.

## Side Effects:
- This wrapper itself performs no direct I/O or global mutations beyond instantiating an object and calling its method.
- All observable side effects are produced by CSVSQL.run(), and may include:
  - Reading CSV input and converting to SQL or executing SQL statements.
  - Creating, modifying, or connecting to a database via SQLAlchemy or other drivers.
  - Writing output to stdout, files, or a database.
  - Printing diagnostic messages to stderr.
  - Launching interactive prompts or blocking operations if CSVSQL.run implements them.
  - Raising SystemExit or other exceptions that propagate to the caller.

## Control Flow:
flowchart TD
    A[Call launch_new_instance()] --> B[Instantiate CSVSQL()]
    B --> C{CSVSQL.__init__ succeeds?}
    C -- no --> D[Constructor exception propagates to caller]
    C -- yes --> E[Call CSVSQL.run()]
    E --> F{CSVSQL.run() completes normally?}
    F -- yes --> G[Function returns None]
    F -- no --> H[Runtime exception or SystemExit propagates to caller]

## Examples:
- Packaging entry-point (conceptual):
  - Register csvkit.utilities.csvsql:launch_new_instance as a console_scripts entry point so the packaging/runtime imports the module and calls launch_new_instance() to start the installed "csvsql" command.

- Programmatic invocation with error handling:
  - Use from tests or harnesses to run the utility and capture expected failures:
      try:
          launch_new_instance()
      except NameError:
          # CSVSQL class not available in this runtime/module
          handle_missing_entry_point()
      except SystemExit:
          # Argument parser or command logic triggered process exit
          handle_exit_condition()
      except Exception as exc:
          # Other runtime errors from CSVSQL.run() such as I/O, SQLAlchemy, or parsing errors
          handle_runtime_error(exc)

Notes:
- This wrapper intentionally remains minimal and delegates operational responsibilities to CSVSQL and the underlying CLI framework. For details about CLI options, argument parsing behavior, SQL execution semantics, and exact side effects, consult the CSVSQL component and CSVKitUtility.run documentation.

