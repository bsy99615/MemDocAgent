# `sql2csv.py`

## `csvkit.utilities.sql2csv.SQL2CSV` · *class*

## Summary:
SQL2CSV is a command-line utility class that executes an SQL query against a database (via SQLAlchemy) and writes the query result set to a CSV output using agate's CSV writer.

## Description:
SQL2CSV is intended to be used as a CLI command implementation inside csvkit's CLI framework (it subclasses CSVKitUtility). Typical instantiation is performed by csvkit's CLI entrypoint or test harness that creates the utility, invokes add_arguments to register CLI flags, parses arguments into self.args, and then calls main() to perform the work.

Primary responsibilities:
- Define and register command-line arguments specific to executing SQL and controlling CSV output.
- Connect to a database using SQLAlchemy create_engine with the given connection string.
- Obtain the SQL query to execute from (in priority): --query, an input file argument, or piped STDIN.
- Execute the SQL query in a mode that prohibits parameter binding (execution_options(no_parameters=True)) and stream rows.
- Write rows to the configured output_file as CSV using agate.csv.writer, optionally writing the header row.

This class encapsulates only CLI parsing for SQL execution and result writing; connection creation, execution, and CSV writing are performed directly in main() and are not delegated to helper objects beyond CSVKitUtility helpers (additional_input_expected, _open_input_file) and SQLAlchemy/agate APIs.

## State:
Class attributes:
- description (str)
  - Value: 'Execute an SQL query on a database and output the result to a CSV file.'
  - Purpose: human-readable description used in CLI help output.

- override_flags (list[str])
  - Value: the list produced by splitting 'f,b,d,e,H,K,L,p,q,S,t,u,z,blanks,date-format,datetime-format,zero' on commas.
  - Purpose: indicates flags from the CSV writer/CSVKitUtility that this command overrides or manages specially.

Instance attributes (inherited or set at runtime):
- argparser (argparse.ArgumentParser)
  - Provided by CSVKitUtility base class. SQL2CSV.registers arguments on this parser in add_arguments().

- args (argparse.Namespace)
  - Populated after argument parsing. Fields referenced by SQL2CSV.main():
    - connection_string (str): default 'sqlite://'. The sqlalchemy connection string to pass to create_engine.
    - input_path (str | None): file path argument for a file containing the SQL query; falsy means read from STDIN.
    - query (str | None): inline SQL query provided with --query; if present it overrides FILE/STDIN.
    - encoding (str): default 'utf-8'; used when opening input files / reconfiguring stdin.
    - no_header_row (bool): True when user passed -H/--no-header-row to suppress column names in output.

- input_file (TextIO or LazyFile) — created during main() only when reading a query from a file/STDIN.
  - Type: sys.stdin or a LazyFile that opens a file in text mode. Valid after main() sets it; otherwise absent.
  - If created from a filesystem path it may raise file-related exceptions when first opened by LazyFile.

- output_file (TextIO)
  - Provided by CSVKitUtility; the destination stream for CSV output (stdout by default in typical CLI runs). Must be present for writing.

- writer_kwargs (dict)
  - Provided by CSVKitUtility; contains CSV writer configuration values. add_arguments() sets defaults (many set to None) to delegate to base-class handling.

Invariants:
- Before main() attempts to write CSV, output_file and writer_kwargs must exist and be correctly configured by the CSVKitUtility base class and argument parsing.
- add_arguments() must be invoked before parsing user input so args contains the described attributes.

## Lifecycle:
Creation:
- Instantiate via the CSVKitUtility-compatible constructor (SQL2CSV does not define its own __init__). No additional constructor parameters are required by SQL2CSV; it inherits the base constructor behavior.

Typical usage sequence:
1. Instantiate SQL2CSV (constructor inherited).
2. Call add_arguments() to register SQL2CSV-specific CLI flags onto argparser (usually done by the surrounding CLI framework).
   - Registers: --db (connection_string, default 'sqlite://'), positional FILE -> input_path, --query, -e/--encoding (encoding default 'utf-8'), -H/--no-header-row (no_header_row flag).
   - Also calls argparser.set_defaults(...) to set writer-related defaults (delimiter, doublequote, escapechar, field_size_limit, quotechar, quoting, skipinitialspace, tabs and encoding default).
3. Parse CLI args into self.args (performed by the framework).
4. Call main() to perform the query and write CSV:
   - Validate input expectations via additional_input_expected() vs args.query; error out if input is expected but no query/file provided.
   - Create a SQLAlchemy Engine via create_engine(self.args.connection_string). If import of a backend module required by the connection string fails, SQL2CSV captures ImportError and re-raises an ImportError with a descriptive message about missing DB backend packages.
   - Open a connection with engine.connect().
   - Determine the SQL query: prefer self.args.query (stripped), otherwise read the whole input file/STDIN into a single query string using self._open_input_file(self.args.input_path) and iterating its lines. input_file is closed after reading.
   - Execute the SQL: connection.execution_options(no_parameters=True).exec_driver_sql(query) and assign result to rows.
   - Create an agate CSV writer with agate.csv.writer(self.output_file, **self.writer_kwargs).
   - If rows.returns_rows is truthy:
       - Unless args.no_header_row is set, write the header row from rows._metadata.keys.
       - Iterate rows and write each row with output.writerow(row).
   - Close the connection and dispose the engine (connection.close(); engine.dispose()).

Destruction / cleanup:
- main() closes the DB connection and calls engine.dispose() on successful execution. There is no explicit exception-safe finalizer in main(); if an exception occurs before cleanup, connection and engine may remain open unless the surrounding framework handles process exit.
- input_file is closed explicitly after reading the query when the query was read from a file/STDIN in the "else" branch.
- There is no context manager provided by SQL2CSV itself; resource cleanup is done manually in main().

## Method Map:
Graph of primary method invocations and flows (Mermaid-style flowchart):
flowchart TD
  A[add_arguments()] --> B[argparser.set_defaults(...)]
  C[main()] --> D[additional_input_expected()]
  C --> E[create_engine(connection_string)]
  E --> F[engine.connect()]
  C --> G[_open_input_file(input_path)] --> H[read lines into query string] --> I[input_file.close()]
  F --> J[connection.execution_options(no_parameters=True)]
  J --> K[exec_driver_sql(query)] --> L[rows]
  L --> M[agate.csv.writer(output_file, **writer_kwargs)]
  L --> N{rows.returns_rows?}
  N -->|true| O[maybe write header: rows._metadata.keys]
  N -->|true| P[for row in rows: output.writerow(row)]
  C --> Q[connection.close()]
  C --> R[engine.dispose()]

## Raises:
Exceptions that may be raised directly by operations in SQL2CSV.main() and their typical triggers:
- SystemExit (via argparse error):
  - Triggered by argparser.error('You must provide an input file or piped data.') when additional_input_expected() is true and --query was not provided. The underlying argparse behavior exits the program (SystemExit).

- ImportError (re-raised with explanatory message):
  - When create_engine() attempts to import a DB backend (e.g., psycopg2 for PostgreSQL) but the backend-specific module isn't installed, SQLAlchemy may raise ImportError which SQL2CSV catches and re-raises as an ImportError with a user-facing explanatory message and suggestions.

- SQLAlchemy engine/connection exceptions (e.g., sqlalchemy.exc.SQLAlchemyError):
  - create_engine(connection_string) or engine.connect() can raise SQLAlchemy errors for malformed connection strings, network/authentication problems, missing drivers, or other driver-specific issues.
  - Executing exec_driver_sql(query) can raise SQL syntax errors or driver-level exceptions.

- File/IO exceptions:
  - When input_path refers to a filesystem path wrapped by LazyFile, reading the file may raise FileNotFoundError, PermissionError, OSError, etc., at the time the LazyFile is first read (not when _open_input_file is called).
  - If stdin.reconfigure is invoked by _open_input_file and stdin lacks reconfigure, an AttributeError could be raised from the helper method.

- AttributeError:
  - If expected attributes on self.args (e.g., input_path, encoding, connection_string) are missing because add_arguments() was not run or the argument parser was configured differently, attribute access may raise AttributeError.

- Any exception from agate.csv.writer or output.writerow (e.g., UnicodeEncodeError, IOError):
  - Writing to output_file may raise I/O or encoding errors if the output stream cannot accept the data or encoding conversion fails.

Notes about cleanup on exceptions:
- main() performs connection.close() and engine.dispose() at the end of its normal path. If exceptions are raised before those calls, they will not be executed; callers should run the utility within a framework that ensures process-level cleanup or wrap invocation in try/finally if persistent connections/resources must be freed.

## Example (how to use / reimplement):
- Set up a CSVKitUtility-compatible CLI harness that:
  1. Instantiates SQL2CSV (no custom constructor args required).
  2. Calls add_arguments() so the SQL2CSV options --db (--connection_string), FILE (input_path), --query, -e/--encoding, and -H/--no-header-row are registered.
  3. Parses the command-line into sql2csv.args (making sure output_file and writer_kwargs are configured by the base class).
  4. Calls sql2csv.main().

Typical invocation scenarios:
- Inline query to stdout:
  - Provide --db "postgresql://user:pass@host/db" and --query "SELECT id, name FROM users;" and let the utility write CSV to stdout.
- Query from file:
  - Provide a FILE containing the SQL and optionally --db to connect; main() will read the whole file into a single SQL string and execute it.
- Piped SQL via STDIN:
  - If no FILE is supplied and STDIN is piped (not an interactive tty), the utility will read the piped SQL from stdin and execute it. If the CLI is run interactively (stdin is a tty) and no --query/file is provided, main() will call argparser.error and exit with a message instructing the user to provide input.

Implementation pointers for reimplementation:
- Reuse CSVKitUtility helpers for argument registration, input file opening semantics (_open_input_file), and determining whether additional input is expected.
- Use SQLAlchemy's create_engine and engine.connect() to obtain a connection; call connection.execution_options(no_parameters=True).exec_driver_sql(query) to execute a raw SQL string without parameter binding.
- Use agate.csv.writer(output_file, **writer_kwargs) for CSV output and write header from rows._metadata.keys when rows.returns_rows is true and headers are not suppressed.
- Ensure to close connection and call engine.dispose() after normal execution; consider wrapping execution in try/finally to guarantee cleanup on exceptions if desired.

### `csvkit.utilities.sql2csv.SQL2CSV.add_arguments` · *method*

## Summary:
Mutates the instance argument parser by registering sql2csv-specific command-line options and by setting a set of CSV-related parser default values.

## Description:
This method performs only argument registration on self.argparser. It does not parse arguments or perform any I/O. There are no callers shown in this file; the method is intended to be invoked during CLI setup by whatever code constructs and prepares the utility's argument parser prior to parsing (the exact caller is external to this file). The separation of argument registration into its own method keeps parser configuration localized and reusable.

## Args:
This method takes no arguments and returns None. It operates by mutating self.argparser.

Arguments registered on self.argparser (each bullet corresponds to one call to add_argument in the source):

- --db
  - dest: connection_string
  - type: string
  - default: 'sqlite://'
  - help: 'An sqlalchemy connection string to connect to a database.'
  - Effect: Provides a connection string value under the name connection_string on the parsed namespace.

- FILE (positional)
  - metavar: 'FILE'
  - nargs: '?'
  - dest: input_path
  - type: string
  - default: (implicit None if omitted)
  - help: 'The file to use as SQL query. If FILE and --query are omitted, the query is piped data via STDIN.'
  - Effect: Supplies an optional positional input_path representing a file containing an SQL query.

- --query
  - dest: query (implicit)
  - type: string
  - default: (implicit None if omitted)
  - help: "The SQL query to execute. Overrides FILE and STDIN."

- -e, --encoding
  - dest: encoding
  - type: string
  - default: 'utf-8'
  - help: 'Specify the encoding of the input query file.'

- -H, --no-header-row
  - dest: no_header_row
  - action: store_true
  - default: False (implicit; action store_true sets True when present)
  - help: 'Do not output column names.'
  - Effect: When provided on the command line, the namespace attribute no_header_row will be True.

Parser-level defaults set via set_defaults (key: value as set on the parser object):
- delimiter: None
- doublequote: None
- escapechar: None
- encoding: 'utf-8'
- field_size_limit: None
- quotechar: None
- quoting: None
- skipinitialspace: None
- tabs: None

## Returns:
None. The method does not return a value; it mutates self.argparser.

## Raises:
- AttributeError: If self.argparser is not present on self or does not expose add_argument or set_defaults, attribute access will raise AttributeError.
- Any exception raised by the underlying parser implementation (for example, errors thrown by parser.add_argument or parser.set_defaults) will propagate out of this method unchanged. This method does not catch or wrap such exceptions.

## State Changes:
Attributes READ:
- self.argparser (the method calls methods on this attribute and therefore reads it)

Attributes WRITTEN:
- self.argparser (the parser object is modified by add_argument and set_defaults calls; those modifications mutate the parser's internal registration and defaults)

No other attributes on self are read or written.

## Constraints:
Preconditions:
- self.argparser must exist and must provide methods compatible with argparse.ArgumentParser semantics: add_argument(...) and set_defaults(...).
- The parser should not already have conflicting registrations for the same option strings if a duplicate registration would be unacceptable in the application context.

Postconditions:
- After the call, the parser referenced by self.argparser will accept the options listed above and will have the listed default keys set on its defaults mapping.
- The namespace produced by a subsequent parse_args() on this parser will contain attributes connection_string, input_path, query, encoding, no_header_row (and any other parser defaults set) based on user input and the defaults defined here.

## Side Effects:
- Mutates the parser object reachable via self.argparser in memory.
- No file, network, or database operations are performed.
- No global state is modified by this method beyond the mutations on the parser instance.

### `csvkit.utilities.sql2csv.SQL2CSV.main` · *method*

## Summary:
Execute an SQL statement against a database and stream any returned rows as CSV to the utility's output stream; when reading the query from a file, sets self.input_file while reading and closes it before returning.

## Description:
This is the runtime entry point that performs the SQL2CSV utility's core workflow: validate required input, create an SQLAlchemy engine, open a connection, obtain the SQL query (either from the --query argument or by reading the input file/STDIN), execute the query without parameter binding, and write returned rows to the configured CSV output using agate.

Known callers and context:
- Invoked by the CSVKit command-line runner when executing the SQL2CSV command. It is the lifecycle stage where the command actually performs I/O, database access, and CSV emission after argument parsing and option handling.

Why this is a separate method:
- Centralizes end-to-end execution logic (input validation, engine/connection lifecycle, query acquisition, execution, CSV output, and cleanup) so resource management and error handling are kept together rather than scattered across helpers.

## Args:
- None (operates on instance attributes populated prior to invocation).
  Relies on these instance fields (names and expected types):
  - self.args.connection_string (str): SQLAlchemy connection string; default provided by add_arguments ('sqlite://').
  - self.args.query (str|None): SQL provided via --query; if present, it is used directly (with whitespace trimmed).
  - self.args.input_path (str|None): Path to a file containing SQL; passed to self._open_input_file when --query is not provided.
  - self.args.encoding (str): Encoding for reading input files (default 'utf-8').
  - self.args.no_header_row (bool): When True, suppress writing the header row.
  - self.output_file (file-like): Destination stream for CSV output.
  - self.writer_kwargs (dict): Keyword arguments forwarded to agate.csv.writer.

## Returns:
- None. The method writes CSV data into self.output_file and does not return a value.

## Raises:
- SystemExit: Triggered indirectly by calling self.argparser.error('You must provide an input file or piped data.') when additional_input_expected() returns True and self.args.query is falsy. (argparse.ArgumentParser.error prints an error message and raises SystemExit.)
- ImportError: If create_engine(self.args.connection_string) raises ImportError (commonly because the DB-API/dialect required by the connection string is not installed), the method re-raises an ImportError with an explanatory message and suggestions for common backends; the original ImportError is chained as the cause.

## Behavior and Edge Cases:
- Query selection:
  - If self.args.query is truthy, the method uses self.args.query.strip() (leading/trailing whitespace removed) as the SQL to execute.
  - Otherwise, it calls self._open_input_file(self.args.input_path), assigns the returned file-like object to self.input_file, reads all lines from it (concatenating them in order) to produce the query string, and closes self.input_file before proceeding.
- Execution:
  - The code executes connection.execution_options(no_parameters=True).exec_driver_sql(query), which executes the SQL string and returns an object referenced as rows.
  - If rows.returns_rows is True, the method writes results to CSV:
    - Unless self.args.no_header_row is True, it writes a header row using rows._metadata.keys.
    - It then iterates rows and writes each row as a CSV row.
  - If rows.returns_rows is False, no header or row data is written.
- Resource cleanup:
  - The method calls connection.close() and engine.dispose() before returning, ensuring DB resources are released.

## State Changes:
Attributes READ:
- self.args (reads connection_string, query, input_path, encoding, no_header_row)
- self.argparser (used to report missing input)
- self.writer_kwargs (passed to agate.csv.writer)
- self.output_file (passed to agate.csv.writer)
- self._open_input_file (method invoked when reading query from input_path)
- self.additional_input_expected (method invoked to determine if input is required)

Attributes WRITTEN:
- self.input_file: set to the file-like object returned by self._open_input_file(self.args.input_path) when --query is not supplied. That file is explicitly closed within the method before returning.

## Constraints:
Preconditions:
- self.args and self.argparser must be initialized (typically by argument parsing).
- self.output_file and self.writer_kwargs must be valid and suitable for agate.csv.writer.
- Methods self._open_input_file and self.additional_input_expected must exist on the instance.
- self.args.connection_string should be a string acceptable to SQLAlchemy's create_engine.

Postconditions:
- The SQL in query (from --query or the opened input file) has been executed.
- If the statement returned rows, header and data rows (subject to no_header_row) will have been written to self.output_file.
- connection.close() and engine.dispose() will have been called.
- If self.input_file was opened, it will be closed and the attribute will reference the last opened file object (which is closed).

## Side Effects:
- I/O:
  - May open and read an input file/STDIN via self._open_input_file(self.args.input_path).
  - Writes CSV output to self.output_file via agate.csv.writer using self.writer_kwargs.
- External library interactions:
  - Calls SQLAlchemy create_engine(...) which may import DB-API modules and create an engine object.
  - Opens a live database connection (engine.connect()) and executes SQL via exec_driver_sql.
- Process control:
  - Calls self.argparser.error(...) to report missing input; argparse.ArgumentParser.error prints usage and message, then raises SystemExit (terminating the process) unless caught upstream.

## `csvkit.utilities.sql2csv.launch_new_instance` · *function*

## Summary:
Instantiate the SQL-to-CSV CLI utility and hand control to its run lifecycle so the SQL execution and CSV output behavior implemented by SQL2CSV is executed.

## Description:
- Known callers and typical contexts:
  - Packaging entry points (console_scripts) that boot the installed sql2csv command at process start.
  - Test harnesses and integration tests that run the utility in-process to exercise end-to-end SQL execution and CSV output behavior.
  - Any programmatic runner that wants a zero-argument entry point to start SQL2CSV without referencing the class name.

- Typical trigger:
  - The runtime imports the module and calls this function with no arguments at process start (or a test calls it) to begin the SQL2CSV lifecycle: argument parsing (via CSVKitUtility base class), input acquisition, SQL execution, and CSV writing.

- Why this wrapper exists:
  - Provides a stable, importable, and testable bootstrap function that hides SQL2CSV instantiation and invocation details from packaging/test code.
  - Keeps bootstrapping separate from the utility implementation so callers do not need to know the class name or call run() themselves.
  - Keeps a uniform convention among csvkit utilities: a minimal launch_new_instance that constructs the utility and lets its run() method manage the full lifecycle.

## Args:
- None.

## Returns:
- None.
  - The function returns implicitly after SQL2CSV.run() completes normally.
  - If SQL2CSV.run() blocks (for example awaiting input or performing a long-running query), this function will block until run() returns or raises.
  - No success value is returned; callers must infer success from absence of exceptions or external side effects (written CSV, exit code, printed messages).

## Raises:
- NameError
  - Condition: The name SQL2CSV is not defined or importable in the module namespace when launching (attempting to call SQL2CSV() will raise NameError).

- Any exception raised by SQL2CSV.__init__
  - Condition: constructor-time failures (for example, errors raised by CSVKitUtility base constructor or subclass initialization) will propagate unchanged.

- Any exception raised by SQL2CSV.run()
  - Conditions and common examples (originating from SQL2CSV.main()/run rather than this wrapper):
    - SystemExit: triggered by argument parsing errors (argparse.error) when required input is missing or invalid.
    - ImportError: missing DB backend packages when SQLAlchemy attempts to import a driver required for the provided connection string.
    - SQLAlchemy exceptions (e.g., sqlalchemy.exc.SQLAlchemyError): malformed connection strings, authentication failures, network/connectivity errors, or execution-time errors.
    - File/IO exceptions (FileNotFoundError, PermissionError, OSError): when opening an input file or writing to the configured output stream.
    - AttributeError: if expected args attributes (such as input_path, connection_string, no_header_row) are absent because argument registration or parsing did not occur.
    - agate/csv writer or encoding errors (UnicodeEncodeError, IOError) during CSV output.

## Constraints:
- Preconditions:
  - SQL2CSV must be available in the module scope (typically via module-level imports).
  - Any runtime context expected by SQL2CSV.run() must be in place (for example, sys.argv for argument parsing, environment variables, or access to input files).
  - The caller should ensure that necessary dependencies (database drivers, agate) are installed for the intended connection string and CSV operations.

- Postconditions:
  - If the function returns normally, SQL2CSV.run() has completed and its side effects (database queries executed, CSV output written to the configured output_file, opened input files closed where applicable) have occurred.
  - No value is returned to indicate success; resources created or modified by SQL2CSV (DB connections closed in the normal path, engines disposed) will have been handled as implemented by SQL2CSV.run().

## Side Effects:
- This wrapper performs only object instantiation and a direct method call. All observable side effects are produced by SQL2CSV.run(), which commonly include:
  - Creating a SQLAlchemy Engine via create_engine(connection_string) and opening a Connection.
  - Executing SQL via connection.execution_options(no_parameters=True).exec_driver_sql(query).
  - Writing query results to the configured output_file using agate.csv.writer (including optionally writing a header row).
  - Opening and reading an input file or stdin to obtain an SQL query string.
  - Closing database connections and disposing the engine on the normal execution path.
  - Emitting stdout/stderr output and possibly exiting the process with SystemExit on parse errors.

## Control Flow:
flowchart TD
    A[Call launch_new_instance()] --> B[Instantiate SQL2CSV()]
    B --> C{SQL2CSV.__init__ succeeds?}
    C -- no --> D[Constructor exception propagates to caller]
    C -- yes --> E[Call SQL2CSV.run()]
    E --> F{SQL2CSV.run() completes normally?}
    F -- yes --> G[Function returns None]
    F -- no --> H[Runtime exception (ImportError, SQLAlchemyError, SystemExit, IOError, etc.) propagates to caller]

## Examples:
- Packaging / entry point (conceptual):
  - Register this function as a console_scripts entry point so the packaging runtime imports the module and calls launch_new_instance() to start the installed sql2csv command. The packaging layer is responsible for process startup; this function simply constructs and runs the utility.

- Programmatic invocation with basic error handling (description):
  - Call launch_new_instance() from a test harness or integration runner and handle expected exceptions rather than letting them terminate the process. Typical exceptions to catch are SystemExit (argument parsing), ImportError (missing DB driver), FileNotFoundError (missing SQL input file), and SQLAlchemyError (connection or execution failures). Wrap invocation in a try/except that logs or asserts on the exception types relevant to the caller's needs.

Notes:
- The wrapper intentionally does not perform validation, argument parsing, or resource cleanup itself beyond delegating to SQL2CSV.run(). For precise behaviors (which CLI flags are registered, how SQL is sourced, exact cleanup semantics, and what exceptions SQL2CSV.run() may raise), consult the SQL2CSV component documentation.

