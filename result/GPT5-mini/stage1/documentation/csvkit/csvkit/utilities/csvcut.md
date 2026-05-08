# `csvcut.py`

## `csvkit.utilities.csvcut.CSVCut` · *class*

## Summary:
Represents the csvcut CLI command: extract, reorder, or remove columns from CSV input and write the truncated table to output (similar to Unix cut but for CSV/tabular data).

## Description:
CSVCut is a small command-class intended to be executed as part of csvkit's CLI framework. It:
- Exposes CLI options for listing column names, selecting columns to include or exclude, and optionally deleting rows that become completely empty after cutting.
- Reads CSV input (file or stdin) using the shared CSVKit input helpers, resolves user-specified column selectors to concrete 0-based indices, and writes only the requested columns to the configured output stream.

When to instantiate:
- As part of csvkit's CLI plumbing (e.g., the program entrypoint constructs the utility and calls its run/main lifecycle).
- Unit tests may instantiate it directly (providing mocked file-like objects and a pre-populated args object) to test behavior without invoking a subprocess.

Why this class exists:
- Encapsulates column-selection and row-truncation behavior for CSV output; separates CLI parsing (add_arguments), high-level command logic (main), and reusable CSV handling (delegated to CSVKitUtility helpers). CSVCut focuses on how to transform rows based on column selectors and the --delete-empty option.

Responsibility boundary:
- CSVCut is responsible for: registering its specific CLI flags, invoking shared CSV-reading helpers, mapping resolved column indices to output rows, respecting the delete-empty option, and emitting CSV output via agate.csv.writer.
- It delegates header and column-resolution, stdin/file handling, skipped-line logic, and CSV reader/writer configuration to its CSVKitUtility base class and helper methods.

## State:
Attributes used or relied upon (inherited from CSVKitUtility unless noted):
- description (str, class attribute)
    - Human-readable command description.
- override_flags (list[str], class attribute)
    - Flags to suppress or override in base parser (inherited static config).
- argparser (argparse.ArgumentParser-like)
    - Populated by the base class. Used by add_arguments to register flags.
- args (argparse.Namespace-like)
    - Values parsed from CLI. Relevant attributes:
        - names_only (bool): True when -n/--names requested.
        - columns (str | None): Raw selector string passed with -c/--columns.
        - not_columns (str | None): Raw selector string passed with -C/--not-columns.
        - delete_empty (bool): True when -x/--delete-empty requested.
        - no_header_row, zero_based, input_path, skip_lines, and other CSV-related flags are read by delegated helpers.
- reader_kwargs (dict)
    - Mapping forwarded to agate.csv.reader. Common keys: delimiter, quotechar, header, etc.
- writer_kwargs (dict)
    - Mapping forwarded to agate.csv.writer. Controls CSV quoting/encoding for output.
- input_file (file-like, readable)
    - Underlying input stream; prepared by base-class run logic before main() is invoked.
- output_file (file-like, writable)
    - Where agate.csv.writer writes output rows.
- (transient) column_names (list[str]) and column_ids (iterable[int])
    - Local values returned by get_rows_and_column_names_and_column_ids and used within main.
    - Invariant: each value in column_ids is a non-negative integer and satisfies 0 <= idx < len(column_names) (when column_names is non-empty). column_ids are 0-based indices.

Class invariants:
- Before main executes, the base-class initialization must have set up argparser, args, reader_kwargs, writer_kwargs, input_file, output_file and skip_lines semantics.
- When main calls get_rows_and_column_names_and_column_ids, that helper returns:
    - rows: an iterator yielding subsequent CSV rows (each row is a sequence of cell strings)
    - column_names: sequence of header labels (possibly generated defaults)
    - column_ids: resolved list/range of 0-based indices
- The writer created via agate.csv.writer(self.output_file, **self.writer_kwargs) accepts writer.writerow(iterable) calls where each element is serializable by the agate writer.

## Lifecycle:
Creation:
- Instantiate via the CSVKitUtility constructor (CSVCut has no custom __init__). The base constructor is expected to initialize argument parsing and file/IO attributes. Typical callers:
    - CLI entrypoint which builds and runs the utility.
    - Test harnesses that construct the class and inject args, input_file, and output_file.

Usage (typical sequence):
1. add_arguments() — called by CLI framework during setup to register flags:
    - -n/--names -> names_only
    - -c/--columns -> columns
    - -C/--not-columns -> not_columns
    - -x/--delete-empty-rows -> delete_empty
2. run() / main() — the command execution path calls main():
    - If args.names_only is True:
        - Delegates to print_column_names() (from CSVKitUtility), which reads the header row and writes numbered column names to output, then exits main early.
    - Otherwise:
        - Calls additional_input_expected(); if that returns truthy, writes a diagnostic line to stderr indicating it's waiting for stdin.
        - Calls get_rows_and_column_names_and_column_ids(**self.reader_kwargs) to obtain:
            - rows: iterator yielding data rows after header/skip lines
            - column_names: sequence of header labels
            - column_ids: sequence or range of 0-based indices to extract
        - Creates a CSV writer via agate.csv.writer(self.output_file, **self.writer_kwargs).
        - Writes a header row containing the selected column names in column_ids order.
        - Iterates rows; for each row:
            - Builds out_row by selecting row[column_id] if column_id < len(row), else None (ensures short rows are padded with None).
            - If args.delete_empty is False, writes out_row unconditionally.
            - If args.delete_empty is True, writes out_row only when any(out_row) is truthy (Python truthiness: None and empty string '' evaluate as falsy).
3. Teardown:
    - CSVCut itself does not perform file closing; the base-run infrastructure is expected to close input and output files (or callers should manage resources).

Destruction / cleanup:
- No context-manager protocol or close() method provided by CSVCut itself. The caller or base class should handle closing file handles and releasing resources.

## Method Map:
A compact call-flow showing how CSVCut.main interacts with helpers and writer:

graph TB
    Main[main()] -->|if names_only| PrintNames[print_column_names()]
    Main -->|else| CheckInput[additional_input_expected()]
    CheckInput -->|maybe writes message| Stderr[sys.stderr.write]
    Main --> GetRows[get_rows_and_column_names_and_column_ids(**reader_kwargs)]
    GetRows --> Rows[(rows iterator), column_names, column_ids]
    Main --> CreateWriter[agate.csv.writer(output_file, **writer_kwargs)]
    CreateWriter --> WriteHeader[writer.writerow(header selected)]
    Main --> LoopRows[for row in rows]
    LoopRows --> BuildOut[out_row = select/pad values by column_ids]
    BuildOut --> Filter[if delete_empty -> any(out_row)]
    Filter --> WriteRow[writer.writerow(out_row)]

(Note: the base-class helpers print_column_names and get_rows_and_column_names_and_column_ids may perform I/O and mutate skip_lines or file read pointers.)

## Raises:
Exceptions may be raised during instantiation or main execution. CSVCut itself does not raise new exception classes beyond what it delegates to; below are the likely exceptions and triggers:

- RequiredHeaderError
    - Trigger: print_column_names() raises this immediately if the utility was configured with --no-header-row and the user requested --names. Occurs when args.no_header_row is truthy and names_only is requested.

- StopIteration
    - Trigger: print_column_names() may propagate StopIteration if the input contains no rows when attempting to read the header. main does not catch this.

- ValueError
    - Trigger: get_rows_and_column_names_and_column_ids raises ValueError if args.skip_lines is not an int (or other parameter validations within helpers).

- ColumnIdentifierError (or similar parse error)
    - Trigger: When user-specified column selectors (args.columns or args.not_columns) cannot be parsed or reference unknown names / out-of-range indices; get_rows_and_column_names_and_column_ids delegates to parse_column_identifiers which may raise.

- AttributeError
    - Trigger: additional_input_expected() may attempt to read args.input_path; if args lacks that attribute due to unusual parser configuration, AttributeError may be raised. Also if sys.stdin lacks isatty or base-class helpers rely on missing attributes.

- agate / CSV parsing exceptions (various)
    - Trigger: agate.csv.reader(...) or agate.csv.writer(...) may raise errors for encoding issues, invalid CSV format, or writer configuration problems. These are propagated.

- I/OError / OSError / BrokenPipeError
    - Trigger: writing to output_file (writer.writerow or sys.stderr.write) may raise standard I/O exceptions (e.g., broken pipe when piping to head). These propagate unless the caller handles them.

Edge behaviors worth noting:
- If a row is shorter than the largest requested column index, CSVCut pads the missing values with None (explicitly checks column_id < len(row) else None).
- When args.delete_empty is True, "empty" is determined by Python truthiness: None and empty strings are falsy; strings containing characters (including "0") are truthy.
- column_ids are 0-based indices. The resolution of user-supplied selectors (which may be numeric or names) is performed by the base helper; CSVCut expects concrete 0-based indices returned by that helper.

## Example:
Typical CLI uses (shell form):

- List column names and indices:
  csvcut --names data.csv
  (prints numbered list of column labels and exits)

- Select columns by index/name/range and write to stdout:
  csvcut -c "1,id,3-5" data.csv > extracted.csv
  (columns are resolved by the shared helper; final written CSV contains only the selected columns in the requested order)

- Exclude columns and drop rows that become empty after cut:
  csvcut -C "password,secret" -x data.csv > redacted.csv
  (removes the named columns, writes remaining columns, and removes any rows that have only empty/falsy values after removal)

- Read from stdin and write to stdout:
  cat data.csv | csvcut -c id,name > result.csv
  (if no input_path provided and stdin is a TTY, the tool may prompt; when piping, it reads stdin directly)

Implementation notes for reimplementation:
- Do not reimplement header parsing or column resolution inside CSVCut; reuse or reproduce the same semantics as:
  - print_column_names: must require a header (raise if args.no_header_row) and number columns according to zero_based flag.
  - additional_input_expected: treat stdin-isatty AND no input_path as an indicator to wait/prompt.
  - get_rows_and_column_names_and_column_ids: must return (rows_iter, column_names, column_ids) where column_ids are 0-based indices derived from args.columns / args.not_columns and column_names length matches the reader-detected column count or produced defaults when --no-header-row is set.
- When writing the header row to output, map column_ids to column_names by index: [column_names[i] for i in column_ids].
- When building each output row, ensure out-of-range column indices produce None entries (so the CSV writer can emit empty fields) rather than IndexError.
- Use agate.csv.writer for the output writer, passing writer_kwargs through to preserve CSV formatting semantics consistent with the rest of csvkit.

### `csvkit.utilities.csvcut.CSVCut.add_arguments` · *method*

## Summary:
Registers four command-line options on the instance argument parser. The call mutates self.argparser so that after argument parsing the Namespace will include the flags names_only, columns, not_columns, and delete_empty which influence CSVCut runtime behavior.

## Description:
This method performs parser-configuration during the CLI setup stage; it does not parse or validate values. It exists to keep all argparse registrations for CSVCut in one place, separate from runtime logic in main().

Known callers and lifecycle:
- Intended to be invoked during CLI setup, before argument parsing.
- CSVCut.main (in the same class) reads the resulting parsed attributes (for example, self.args.names_only and self.args.delete_empty) to decide runtime behavior. This method itself does not call main() or perform parsing.

Why separate:
- Centralizes and documents all CLI options for the command.
- Keeps parsing/validation and runtime processing (main()) separate for readability and easier testing.

## Args (arguments added to self.argparser):
Note: add_arguments takes only self. The following describes the CLI flags it registers; after argparse.parse_args these become attributes on the returned Namespace (commonly available on self.args in this codebase).

- names_only
    - Source flags: -n, --names
    - Dest: names_only
    - Type: bool
    - Action: store_true
    - Default: False
    - Semantics: When True, request that the utility print column names and indices and exit early (handled by main()).

- columns
    - Source flags: -c, --columns
    - Dest: columns
    - Type: str or None
    - Default: None (meaning "all columns" when absent)
    - Format: Comma-separated list of column specifiers. Each item may be:
        * a 1-based integer index (e.g., "1"),
        * a column name (e.g., "id"),
        * or a range "start-end" using 1-based indices (e.g., "3-5").
      Example: "1,id,3-5"
    - Notes: This method only registers the option; parsing/interpretation of this string into numeric indices or names is performed elsewhere in the codebase.

- not_columns
    - Source flags: -C, --not-columns
    - Dest: not_columns
    - Type: str or None
    - Default: None (meaning "exclude no columns" when absent)
    - Format: Same as columns; specifies columns to exclude from the output.
    - Notes: No mutual-exclusion or conflict checking between columns and not_columns is performed here.

- delete_empty
    - Source flags: -x, --delete-empty-rows
    - Dest: delete_empty
    - Type: bool
    - Action: store_true
    - Default: False
    - Semantics: When True, rows that are completely empty after cutting should be omitted from the output (actual deletion logic is implemented in main()).

## Returns:
- None.
- Primary effect: side-effecting registration of the four CLI options on self.argparser.

## Raises:
- AttributeError: If self.argparser does not exist on the instance.
- AttributeError / TypeError: If self.argparser exists but lacks an add_argument method or accepts different parameters, calling add_argument may raise the underlying parser's exceptions.
- Note: This method does not itself validate option values and therefore does not raise parsing/validation errors; those occur later when the parser parses input or when option values are interpreted.

## State Changes:
- Attributes READ:
    - self.argparser (required to call add_argument)
- Attributes WRITTEN / Mutated:
    - self.argparser (its internal state is mutated by registering four new options)
- Indirect / Future state:
    - After parsing (outside this method), the parsed Namespace will contain attributes self.args.names_only, self.args.columns, self.args.not_columns, and self.args.delete_empty. This method does not create or assign self.args.

## Constraints:
- Preconditions:
    - self.argparser must be an argparse.ArgumentParser-like object exposing add_argument.
    - Call this method before parsing arguments and before main() relies on those parsed attributes.
- Postconditions:
    - self.argparser has four additional option definitions corresponding to the documented flags.
    - No additional side-effects on the CSVCut instance beyond the parser mutation.

## Side Effects:
- Mutates the parser object referenced by self.argparser (registers four options).
- No I/O, network access, or modification of files or global state.
- No validation or interpretation of provided option values occurs here.

## Usage examples:
- Extract columns 1, column named "id", and range 3–5:
  csvcut -c 1,id,3-5 input.csv
- Exclude columns 2 and the column named "notes", and remove empty rows:
  csvcut -C 2,notes -x input.csv

## Implementation notes for reimplementation:
- Recreate by calling add_argument on the provided ArgumentParser with:
  - Two store_true boolean flags for names_only (-n/--names) and delete_empty (-x/--delete-empty-rows).
  - Two string-valued options for columns (-c/--columns) and not_columns (-C/--not-columns) with no type coercion.
- Do not perform any parsing or validation of the columns string here; leave that for the component that interprets columns when preparing output.

### `csvkit.utilities.csvcut.CSVCut.main` · *method*

## Summary:
Execute the csvcut command: write a header for the selected columns and stream out each input row truncated/reordered to those columns, honoring options to print only column names or to drop rows that are completely empty after cutting.

## Description:
This is the primary command logic invoked by the CLI runtime after the utility has been configured and input/output resources prepared (CSVKitUtility.run calls this method as the lifecycle step that executes the command-specific behavior). Typical invocation occurs once per CLI execution after argument parsing and resource setup.

The method delegates several responsibilities to helper methods on the same instance:
- print_column_names(): when the --names/-n flag is set, prints column names and indices and exits early.
- additional_input_expected(): used to detect when no input file or piped data was provided; when true the method writes an informational message to standard error.
- get_rows_and_column_names_and_column_ids(**reader_kwargs): returns the rows iterator, the list of column names, and the list of integer column indices to output.

This logic is kept as a dedicated method so that CSVKitUtility.run can uniformly manage resource setup/teardown (open/close of input files, warning suppression) while subclasses implement only their specific processing workflow in main().

## Args:
    None (method has only the implicit self parameter)

## Returns:
    None. The method writes output to self.output_file via an agate CSV writer; it does not return values.

## Raises:
    - IndexError: If any value in column_ids is not a valid index into the column_names list, indexing column_names[column_id] will raise IndexError.
    - Any exception raised by the called helper methods will propagate:
        * Exceptions from get_rows_and_column_names_and_column_ids (I/O, parsing, validation).
        * Exceptions from agate.csv.writer or from writer.writerow (I/O errors on self.output_file, encoding errors, etc.).
        * Exceptions from print_column_names or additional_input_expected if those implementations raise.
    Note: the method itself does not explicitly catch exceptions; callers should expect propagation.

## State Changes:
Attributes READ:
    - self.args: to check options names_only and delete_empty.
    - self.reader_kwargs: passed through to get_rows_and_column_names_and_column_ids.
    - self.writer_kwargs: passed to agate.csv.writer when creating the CSV writer.
    - self.output_file: passed to agate.csv.writer and used as the destination for output.
    - Any attributes accessed/used by get_rows_and_column_names_and_column_ids, print_column_names, or additional_input_expected (these methods are called and may read other attributes).

Attributes WRITTEN:
    - None on self (the method does not assign to self.<attr>). The method writes bytes/text to the external file object referenced by self.output_file but does not mutate self attributes.

## Constraints:
Preconditions:
    - self.args must exist and contain at least:
        * names_only (boolean)
        * delete_empty (boolean)
    - self.reader_kwargs and self.writer_kwargs must be mapping-like objects acceptable to the underlying helper and agate.csv.writer respectively.
    - self.output_file must be an open writable file-like object compatible with agate.csv.writer.
    - get_rows_and_column_names_and_column_ids(**self.reader_kwargs) must return a 3-tuple: (rows, column_names, column_ids), where:
        * rows is an iterable of row sequences (indexable by integer positions).
        * column_names is a sequence (list/tuple) of header strings.
        * column_ids is an iterable of integers referencing positions in column_names and row sequences.
    - If column_ids contains indices >= len(column_names), IndexError may be raised when writing the header.

Postconditions:
    - If self.args.names_only is truthy, the method will call print_column_names() and return without writing to self.output_file.
    - Otherwise, a header row (one value per column_id) will be written to self.output_file with entries column_names[column_id] in the same order as column_ids.
    - Then, for each input row yielded from rows, a row containing entries for each column_id will be written. For any column_id >= len(row) the corresponding output cell will be None.
    - If self.args.delete_empty is truthy, any output row whose cells are all falsy (e.g., None, empty string, 0, False) will be skipped; otherwise all rows are written.
    - The method itself does not close self.output_file.

## Side Effects:
    - Writes a diagnostic message to sys.stderr when additional_input_expected() returns True:
        'No input file or piped data provided. Waiting for standard input:\n'
    - Calls print_column_names(), which typically writes to stdout/stderr (implementation-specific).
    - Calls get_rows_and_column_names_and_column_ids(**self.reader_kwargs) which may perform I/O, parse CSV input, or otherwise produce side effects.
    - Opens a CSV writer via agate.csv.writer(self.output_file, **self.writer_kwargs) and writes the header row and zero or more data rows to self.output_file; this produces I/O on the provided output stream.
    - No mutation of the CSVCut instance attributes is performed by this method itself.

## `csvkit.utilities.csvcut.launch_new_instance` · *function*

## Summary:
Creates and runs a new CSVCut command-line utility instance, bootstrapping the csvcut CLI behavior so the utility executes its parsing and processing lifecycle.

## Description:
- Known callers within the codebase and typical context:
    - No direct internal callers were found. The typical caller is external packaging/entry-point machinery (for example, a console_scripts entry in package metadata) or an integration test that needs to start the csvcut CLI programmatically.
    - Invocation usually occurs at CLI startup time (the packaging runner imports this function and calls it with no arguments) or in tests that call the function to exercise the end-to-end run() behavior of the CSVCut command.

- Why this logic is extracted into its own function:
    - Provides a stable, importable entry point for external runners, packaging entry_points, and tests, without exposing or requiring knowledge of the CSVCut class name or internals.
    - Keeps top-level packaging configuration simple and uniform across csvkit utilities by adopting the one-function bootstrap convention used throughout the utilities package.
    - Separates instantiation/bootstrapping concerns from the CSVCut class itself (which implements CLI parsing, CSV processing, and I/O) so consumers can start the utility with a single call.

## Args:
- This function accepts no arguments.

## Returns:
- None (implicitly). The function does not return any value; the observable effects are produced by CSVCut.run.
- All runtime outcomes (stdout output, file writes, process exit, raised exceptions) are side effects of CSVCut.run and are not returned by this function.

## Raises:
- NameError
    - Condition: CSVCut is not defined in the module namespace (e.g., if the class was not imported or removed), causing instantiation to fail at the call to CSVCut().
- Any exception raised by CSVCut.__init__
    - Condition: constructor raises due to configuration or initialization errors; the exception is propagated unchanged.
- Any exception raised by CSVCut.run (including but not limited to):
    - CSV parsing/encoding errors (agate or underlying CSV reader/writer exceptions)
    - Column resolution errors (e.g., invalid selector leading to a parse/ValueError)
    - I/O errors (OSError, IOError, BrokenPipeError when writing to a closed/invalid stream)
    - SystemExit (if CSVCut.run calls sys.exit)
    - These exceptions are propagated (not caught) by launch_new_instance.

## Constraints:
- Preconditions:
    - The CSVCut class must be defined and importable within the same module before this function is called.
    - Any runtime resources that CSVCut.run expects (such as sys.argv contents, accessible input files, or environment variables) must be in the expected state; launch_new_instance does not validate these resources itself.
- Postconditions:
    - If the function returns normally, CSVCut.run executed to completion (successful end of the command lifecycle).
    - No explicit return value is provided to callers; any process-level exit or side effects have already occurred.

## Side Effects:
- This function itself performs no direct I/O; all side effects are those of CSVCut.run. Typical effects include:
    - Reading CSV input from files or stdin.
    - Writing CSV output to stdout or files via agate.csv.writer.
    - Writing diagnostic or prompt messages to stderr (for example when awaiting stdin).
    - Potentially calling sys.exit (terminating the process) if the utility does so.
    - Raising or propagating exceptions that originate from CSV parsing, column resolution, or I/O operations.

## Control Flow:
flowchart TD
    A[Call launch_new_instance()] --> B[Instantiate CSVCut()]
    B --> C{CSVCut.__init__ succeeds?}
    C -- no --> D[Constructor exception propagates]
    C -- yes --> E[Call CSVCut.run()]
    E --> F{CSVCut.run completes normally?}
    F -- no --> G[Runtime exception or SystemExit propagates]
    F -- yes --> H[launch_new_instance returns None]

## Examples:
- Programmatic invocation with basic error handling:
    try:
        launch_new_instance()
    except Exception as e:
        # Handle initialization or runtime errors raised by the CSVCut utility
        print("csvcut failed:", e, file=sys.stderr)
        raise

- Typical packaging usage (conceptual):
    - Register this function as a console_scripts entry point in package metadata:
        "csvcut = csvkit.utilities.csvcut:launch_new_instance"
    - When the installed command is executed, the packaging runner will import and call launch_new_instance(), which instantiates CSVCut and executes its run lifecycle.

Notes:
- For details about what CSVCut.run does (CLI flags, column resolution, delete-empty behavior, header handling, writer configuration, and specific exceptions raised during processing), see the CSVCut component documentation. This function intentionally delegates all command logic and I/O to that class and does not duplicate its responsibilities.

