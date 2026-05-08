# `csvgrep.py`

## `csvkit.utilities.csvgrep.CSVGrep` · *class*

## Summary:
Represents the csvkit "csvgrep" command: validate CLI options, construct per-column match patterns (regex, literal string, or exact-match file), filter rows using FilteringCSVReader, and write the header plus matching (or inverted-matching) rows to the configured output.

## Description:
CSVGrep is a CLI utility class (subclass of CSVKitUtility) that implements grep-like search semantics for tabular CSV data. It exposes two responsibilities:
- add_arguments: register the command-line options that control which columns to search, the match source (literal string, regular expression, or file of exact-match strings), and matching behavior flags (invert, any-match).
- main: perform the end-to-end execution: validate the parsed arguments, prepare reader/writer options, convert user-specified match input into a per-column pattern mapping, construct a FilteringCSVReader over the input rows, and write the CSV header and resulting rows to the output.

Typical usage:
- In the CSVKitUtility lifecycle, CSVKitUtility (the framework) constructs an instance, calls add_arguments to register CLI flags, parses argv to populate self.args, sets up input/output streams and reader/writer kwargs (self.input_file, self.output_file, self.reader_kwargs, self.writer_kwargs), then invokes main() to perform the search and output results.

Responsibility boundary:
- CSVGrep does not perform CSV parsing directly; it delegates reading to get_rows_and_column_names_and_column_ids (inherited from the base class / framework) and row filtering to FilteringCSVReader.
- It also does not implement CLI parsing itself; it registers arguments and expects the framework to parse them into self.args before main() runs.

Known callers / factories:
- The CSVKitUtility framework (or equivalent command runner) is expected to instantiate CSVGrep, call add_arguments during setup, run the argument parser, and call main() after instance attributes (args, reader_kwargs, writer_kwargs, output_file, etc.) are initialized.

## State:
CSVGrep itself defines no new instance attributes in its own source; it relies on attributes provided by CSVKitUtility. The following attributes are read or mutated by its methods. Implementers must ensure these are present with the documented types/constraints before calling main().

Required instance attributes (read by CSVGrep.main and add_arguments):
- argparser (argparse.ArgumentParser-like)
  - Type: object with add_argument(...) and error(msg) methods
  - Constraint: add_arguments mutates it to register CLI options; error(msg) is used to exit on invalid arguments.
- args (argparse.Namespace-like)
  - Attributes read:
    - names_only (bool) — default False. If True, main() calls print_column_names() and returns.
    - columns (str or falsy) — comma-separated column selectors (required unless names_only).
    - regex (str or None) — regular expression string to compile and use as a matcher (mutually exclusive with other match sources in practice).
    - pattern (str or None) — literal string to match.
    - matchfile (file-like or None) — opened file object; if provided, all lines (rstrip) become the exact-match set. main() will close this file.
    - inverse (bool) — default False. If True, filtering is inverted (select non-matching rows).
    - any_match (bool) — default False. If True, a row matches when any of the specified columns matches rather than requiring all columns to match.
- reader_kwargs (dict)
  - Type: dict of keyword arguments forwarded to the CSV reader and to get_rows_and_column_names_and_column_ids.
  - Mutations: CSVGrep.main may set reader_kwargs['line_numbers'] = True when writer_kwargs requests line_numbers. This is done in-place (reader_kwargs is used by the surrounding framework).
- writer_kwargs (dict)
  - Type: dict of keyword arguments forwarded to the CSV writer (agate.csv.writer).
  - Mutations: CSVGrep.main will pop the 'line_numbers' key if present. After main(), writer_kwargs will no longer contain that key.
- output_file
  - Type: writable file-like object (e.g., open file or sys.stdout) acceptable for agate.csv.writer(output_file, **writer_kwargs).
  - Constraint: must be open for writing and support write/flush as needed.
- get_rows_and_column_names_and_column_ids (callable)
  - Signature: callable(**reader_kwargs) -> (rows_iterable, column_names, column_ids)
  - Return semantics:
    - rows_iterable: iterator over data rows (each row is a sequence of cell values; header is not included by rows_iterable because header=False is later passed to FilteringCSVReader).
    - column_names: sequence of header strings to be written as the CSV header.
    - column_ids: iterable of column identifiers used to build the patterns mapping; exact type is determined by the framework (commonly integer indices or header names).
- print_column_names (callable)
  - Signature: callable() -> None
  - Purpose: invoked when args.names_only is True to display column names and indices and then exit. Any exceptions raised by this method propagate.
- additional_input_expected (callable)
  - Signature: callable() -> bool
  - Purpose: When True, main() writes an informational message to sys.stderr warning that it is waiting for stdin.

Class-level attributes:
- description (str): "Search CSV files. Like the Unix "grep" command, but for tabular data."
- override_flags (list[str]): ['L', 'blanks', 'date-format', 'datetime-format']

Class invariants:
- Before calling main(), implementers must ensure args, argparser, reader_kwargs, writer_kwargs, output_file and the helper callables exist and conform to the types described above.
- add_arguments must be called before argument parsing so the parser registers the expected flags. The framework typically calls this when building the parser.

## Lifecycle:
Creation:
- Instantiate via the surrounding CLI framework (CSVKitUtility or equivalent). CSVGrep has no custom __init__; required state is injected by the framework after construction.
- Required initial setup prior to calling main():
  1. call add_arguments() and parse CLI arguments into args (framework responsibility),
  2. set reader_kwargs and writer_kwargs (dicts),
  3. set output_file (writable),
  4. provide get_rows_and_column_names_and_column_ids, print_column_names, and additional_input_expected via inheritance or framework wiring.

Usage (typical method call sequence):
1. add_arguments() — called during parser construction to register CLI options.
2. (Framework parses argv and populates self.args)
3. main() — performs the operation
   - If args.names_only is True:
     - print_column_names() is called and main() returns early.
   - Otherwise:
     - If additional_input_expected() is True, write a message to sys.stderr.
     - Validate that args.columns is provided; if not, call argparser.error() (exits).
     - Validate that one match source is provided (args.regex, args.pattern, or args.matchfile); otherwise argparser.error() (exits).
     - Prepare reader_kwargs and writer_kwargs; if writer_kwargs contained 'line_numbers', pop it and set reader_kwargs['line_numbers'] = True.
     - Call get_rows_and_column_names_and_column_ids(**reader_kwargs) to obtain (rows, column_names, column_ids).
     - Build a per-column patterns mapping:
         - If args.regex: compile it with re.compile(args.regex) and use the compiled pattern.
         - Elif args.matchfile: build a set(lines.rstrip()) from the file, close the file, and use a predicate function pattern(x) -> bool that returns membership in that set.
         - Else: use args.pattern (literal string) as the pattern value.
       The resulting pattern value may be a compiled regex object, a callable, or a literal string.
     - Instantiate FilteringCSVReader(rows, header=False, patterns=patterns, inverse=args.inverse, any_match=args.any_match).
     - Create an agate CSV writer with agate.csv.writer(self.output_file, **writer_kwargs).
     - Write the column_names as the first output row.
     - Iterate over filter_reader; for each yielded row call output.writerow(row).
Destruction / cleanup:
- main() closes args.matchfile if one was provided (explicitly calls .close()).
- CSVGrep does not implement an explicit destructor or context manager. The surrounding framework is responsible for closing input and output files as needed.
- Any other resources (e.g., rows iterator underlying files) are consumed; exceptions during iteration may leave files open unless the framework manages them.

## Method Map:
graph TD
    A[add_arguments()] --> B[parse args by framework]
    B --> C[main()]
    C -->|if names_only| D[print_column_names()] --> E[return]
    C -->|else| F[additional_input_expected()?] -->|True| G[write stderr message]
    C --> H[validate args.columns and match source] --> I[get_rows_and_column_names_and_column_ids(**reader_kwargs)]
    I --> J[build patterns mapping per column_id]
    J --> K[FilteringCSVReader(rows, header=False, patterns=patterns, inverse=args.inverse, any_match=args.any_match)]
    K --> L[agate.csv.writer(output_file, **writer_kwargs)]
    L --> M[output.writerow(column_names)]
    K --> N[for row in filter_reader: output.writerow(row)]

(Note: This graph represents the primary control and data flow through add_arguments and main. Rectangles are actions; arrows indicate ordering/dependency.)

## Raises:
These are the observable exceptions and the conditions that raise them (as evident from the source):

- SystemExit (via self.argparser.error):
  - Trigger: args.columns is falsy (no columns specified) and names_only is not True.
  - Trigger: none of args.regex, args.pattern, or args.matchfile is provided and names_only is not True.
  - Behavior: argparse.ArgumentParser.error prints a usage-like message and exits; treat this as a SystemExit.

- re.error:
  - Trigger: args.regex is truthy but re.compile(args.regex) fails to compile (invalid regular expression).

- Any exception raised by get_rows_and_column_names_and_column_ids(**reader_kwargs):
  - Trigger: underlying CSV parsing problems, invalid column selectors, I/O errors, or framework-specific validation. These propagate out of main.

- IOError / OSError (or their subclasses):
  - Trigger: reading from args.matchfile (iteration) may raise on I/O failure; closing the file may also raise.
  - Trigger: writing via output.writerow or agate.csv.writer may raise on output I/O errors.

- Any exception raised by FilteringCSVReader (construction or iteration):
  - Trigger: invalid patterns mapping or errors while evaluating patterns for rows. These propagate out of main.

Note: print_column_names may raise its own exceptions (e.g., if headers are missing or parsing failed); when names_only is True these exceptions propagate from main.

## Example:
Below is a concise, stepwise example that demonstrates the intended setup and call sequence (written as a usage recipe rather than raw source code):

1. Framework constructs the utility and sets up parser:
   - Instantiate CSVGrep (framework instantiation; no custom __init__ required).
   - Call csvgrep.add_arguments() so the CLI flags (-n, -c, -m, -r, -f, -i, -a) are registered.
   - Framework parses argv into csvgrep.args (populating names_only, columns, pattern, regex, matchfile, inverse, any_match).

2. Prepare runtime state (done by framework):
   - Ensure csvgrep.reader_kwargs and csvgrep.writer_kwargs are dicts. If the user requested line numbers in output, writer_kwargs may include 'line_numbers': True.
   - Ensure csvgrep.output_file is a writable file-like (e.g., open('out.csv','w') or sys.stdout).
   - Ensure csvgrep.get_rows_and_column_names_and_column_ids exists and, when invoked, returns (rows_iter, column_names, column_ids).

3. Execute:
   - Call csvgrep.main().
     - If args.names_only is True: print_column_names() runs and main returns.
     - Otherwise, main validates arguments; builds a per-column patterns mapping where each value is either:
         - a compiled regex (if -r/--regex was used),
         - a membership predicate function (if -f/--file was used; the file is read and closed), or
         - a literal string (if -m/--match was used).
       Then main constructs a FilteringCSVReader with header=False, patterns=patterns, inverse=args.inverse, any_match=args.any_match; writes the header row; and writes every row yielded by the filter reader.

4. Postconditions:
   - If a matchfile was provided, it has been closed by main().
   - writer_kwargs will have had 'line_numbers' popped off if it existed, and reader_kwargs will have been updated with 'line_numbers': True when appropriate.
   - The output_file contains the header followed by filtered rows (or is partially written if an exception occurred during iteration/writing).

Notes for implementers reimplementing CSVGrep:
- Do not attempt to parse or map the user-provided columns specification within CSVGrep itself — that responsibility belongs to get_rows_and_column_names_and_column_ids (provided by CSVKitUtility or similar). CSVGrep simply requires that method to return column_ids appropriate for constructing the patterns mapping.
- Patterns passed to FilteringCSVReader may be heterogeneous (compiled regex objects, callables, or literal strings). Ensure the filtering component you provide accepts the same or define and document the exact accepted pattern types.
- Respect in-place mutation semantics:
  - Pop 'line_numbers' from writer_kwargs when observed and set reader_kwargs['line_numbers'] = True so downstream readers include line numbers in their rows if requested.
- Be explicit about closing matchfile: when implementing, read all lines and close the file immediately after building the match set to avoid file descriptor leaks.

### `csvkit.utilities.csvgrep.CSVGrep.add_arguments` · *method*

## Summary:
Adds the command-line arguments used by the CSV grep utility to the instance argument parser, mutating the parser's configuration (i.e., registering flags that control matching behavior and which columns to search).

## Description:
This method registers seven command-line options on self.argparser to control how rows are selected from input CSV data:
- A flag to display column names and indices and exit.
- A specification for which columns to search.
- A literal string matcher or a regular-expression matcher.
- A file-based list of exact-match values.
- Flags to invert the match or to require any-column match rather than all columns.

Known callers and context:
- Intended to be called during CLI initialization for the CSVGrep utility class (a CSVKitUtility subclass). In the typical program lifecycle, this method is invoked when the utility builds its ArgumentParser before parsing argv and before running the main processing logic. It exists to keep CLI argument registration separate from parsing and execution logic.

Why this is a separate method:
- Centralizes and documents all CLI options in one place, enabling reuse by the CSVKitUtility framework when constructing the parser and keeping parsing setup decoupled from execution logic.

## Args:
This method takes no arguments beyond self.

The method adds the following command-line options to self.argparser (name / dest / type / behavior / notes):

1. -n, --names
   - dest: names_only
   - type / stored value: bool (True when present)
   - action: store_true
   - behavior: If provided, instructs the utility to display column names and indices and exit.
   - default: False (implicit when using store_true)

2. -c, --columns
   - dest: columns
   - type / stored value: str
   - action: store (default)
   - behavior: A comma-separated list of column identifiers (indices, header names, or ranges) that the grep should search, e.g. "1,id,3-5".
   - default: None (if not provided)

3. -m, --match
   - dest: pattern
   - type / stored value: str
   - action: store
   - behavior: A literal string to search for within the selected columns.
   - default: None

4. -r, --regex
   - dest: regex
   - type / stored value: str
   - action: store
   - behavior: A regular expression (as a string) to match against cell values.
   - default: None

5. -f, --file
   - dest: matchfile
   - type / stored value: file object (open for reading)
   - action: store
   - type converter: argparse.FileType('r') — the parser will open the given path and supply an open file object
   - behavior: For each row, if any line in the provided file (stripped of line separators) exactly equals the cell value, the row is considered a match.
   - default: None
   - notes: The method only registers the argument; it does not read from or close the file.

6. -i, --invert-match
   - dest: inverse
   - type / stored value: bool (True when present)
   - action: store_true
   - behavior: Select non-matching rows instead of matching rows.
   - default: False

7. -a, --any-match
   - dest: any_match
   - type / stored value: bool (True when present)
   - action: store_true
   - behavior: Select rows in which any selected column matches instead of requiring all specified columns to match.
   - default: False

## Returns:
- None. The method's effect is side-effecting: it mutates self.argparser by registering argument definitions.

## Raises:
- The method itself does not explicitly raise exceptions.
- Implicit exceptions may arise from:
  - AttributeError if self.argparser is not set or does not have an add_argument method.
  - argparse-related errors only when the parser is later used to parse arguments (not during registration).

## State Changes:
Attributes READ:
- self.argparser (used to call add_argument)

Attributes WRITTEN / Mutated:
- self.argparser: mutated by multiple calls to its add_argument method (the parser's internal actions list, option strings, and action objects are updated)

## Constraints:
Preconditions:
- self.argparser must be an argparse.ArgumentParser-like object with an add_argument method that accepts the provided parameters.
- The runtime environment must allow argparse.FileType('r') to open files (i.e., provided file paths must be readable when parsed later).

Postconditions:
- After the call, self.argparser will accept the seven options listed above; parsing those options will populate the corresponding attributes on the parsed namespace (names_only, columns, pattern, regex, matchfile, inverse, any_match) with the types described.

## Side Effects:
- Mutates the provided ArgumentParser (self.argparser) by adding argument specifications.
- No I/O is performed by this method itself (it does not open or read files). However, it registers an argument whose parsing (later) will open a file via argparse.FileType('r').
- No network or external service calls are performed.

### `csvkit.utilities.csvgrep.CSVGrep.main` · *method*

## Summary:
Execute the csvgrep command: validate arguments, prepare reader/writer options, build per-column matching patterns (regex, literal string, or matchfile contents), filter rows using FilteringCSVReader, and write the header plus all matching (or inverted-matching) rows to the configured output stream. Returns after printing names-only if requested.

## Description:
This method is the runtime entry point invoked by the CLI command pipeline when the csvgrep utility is executed (typically from CSVKitUtility.run or the CLI entrypoint after argument parsing). It belongs in the main command execution stage where input/output streams and parsed CLI arguments are already available on self.

Known callers and lifecycle stage:
- Called as the command's main handler after CSVKitUtility has parsed command-line arguments and initialized instance attributes (self.args, self.input_file, self.output_file, self.reader_kwargs, self.writer_kwargs, etc.).
- Typical lifecycle: argument parsing -> resource setup -> CSVGrep.main() -> exit. If the user requested names-only (-n), main calls print_column_names() and returns early.

Why this is a separate method:
- Encapsulates end-to-end orchestration for csvgrep: argument validation, converting user options into column indices and patterns, composing the filtering reader, and streaming results. Keeping this logic isolated avoids duplicating command orchestration across utilities and makes it straightforward to test the csvgrep behavior in isolation.

## Args:
None (reads required inputs from instance attributes).

Key instance attributes used (types and expectations):
- self.args: argparse.Namespace-like object with attributes:
    - names_only (bool): if True, print names and exit.
    - columns (str or falsy): comma-separated columns specification required for matching unless names_only.
    - regex (str or None): regular expression to compile and match.
    - pattern (str or None): literal string to match (used directly).
    - matchfile (file-like object or None): opened file object (argparse.FileType('r')) whose stripped lines are used as exact-match values.
    - inverse (bool): invert selection when passed to FilteringCSVReader.
    - any_match (bool): match when any specified column matches rather than all.
- self.argparser: argument parser; used for error(message) which raises a SystemExit.
- self.reader_kwargs (dict): keyword arguments forwarded to get_rows_and_column_names_and_column_ids and ultimately agate.csv.reader.
- self.writer_kwargs (dict): keyword arguments forwarded to agate.csv.writer; may contain 'line_numbers' which is handled specially.
- self.output_file: writable file-like object for CSV output.
- self.get_rows_and_column_names_and_column_ids: method that returns (rows_iter, column_names, column_ids).
- self.print_column_names: helper method invoked when names_only is True.
- self.additional_input_expected: helper that determines whether to prompt/warn about waiting for stdin.

## Returns:
None.

- Normal behavior: writes the header row (column_names) and zero or more data rows matching the criteria to self.output_file and returns None.
- Early return: If args.names_only is True, the method calls self.print_column_names() and returns None immediately (no further validation of columns/regex/pattern/matchfile is performed in that branch).
- No explicit value is returned.

## Raises:
Explicit/observable exceptions and the exact conditions that trigger them:

- SystemExit (via self.argparser.error):
    - Raised if self.args.columns is falsy (no columns were specified) and names_only was not requested.
    - Raised if all of self.args.regex, self.args.pattern, and self.args.matchfile are falsy (no match source provided) and names_only was not requested.
    Note: argparse.ArgumentParser.error prints the message and exits; the effect here is a SystemExit being raised.

- re.error:
    - Raised when re.compile(self.args.regex) is called with an invalid regular expression string and self.args.regex is truthy.

- Any exception propagated from get_rows_and_column_names_and_column_ids:
    - Examples documented by that helper include ValueError (e.g., invalid skip_lines), ColumnIdentifierError (invalid column selectors), I/O or agate.csv.reader parsing errors. These propagate out of main if they occur.

- Any exception raised while reading or closing self.args.matchfile:
    - e.g., IOError/OSError when iterating or closing the file object returned by argparse's FileType('r').

- Any exception raised by FilteringCSVReader creation or iteration:
    - If FilteringCSVReader raises on invalid patterns or on iteration, those exceptions propagate.

- Any exception raised by agate.csv.writer or output.writerow:
    - e.g., I/O errors when writing to self.output_file.

- Note: print_column_names may itself raise RequiredHeaderError or StopIteration; when names_only is True those exceptions will propagate from main.

## State Changes:
Attributes READ:
    - self.args (reads: names_only, columns, regex, pattern, matchfile, inverse, any_match)
    - self.argparser (used to report argument errors)
    - self.reader_kwargs (read to pass into get_rows_and_column_names_and_column_ids)
    - self.writer_kwargs (read to pass into agate.csv.writer and to check/pop 'line_numbers')
    - self.get_rows_and_column_names_and_column_ids (invoked)
    - self.print_column_names (invoked when names_only)
    - self.additional_input_expected (invoked to potentially print a stderr message)
    - self.output_file (used as the target for CSV writing)

Attributes WRITTEN / MUTATED:
    - self.writer_kwargs: mutated by writer_kwargs.pop('line_numbers', False). If a 'line_numbers' key exists, it is removed from the dictionary stored on the instance.
    - self.reader_kwargs: mutated by setting reader_kwargs['line_numbers'] = True when line numbers are requested (propagates to the instance attribute because reader_kwargs is a reference to self.reader_kwargs).
    - self.args.matchfile: the method calls self.args.matchfile.close() when matchfile is provided, which closes the external file object (this mutates external state reachable from the args object).
    - The provided input iterator (rows) is consumed by FilteringCSVReader during iteration (this advances the underlying input file read pointer; the input iterator itself is not replaced on self by this method).

## Constraints:
Preconditions:
    - self.args and self.argparser must be present and correctly initialized by CSVKitUtility.
    - Unless self.args.names_only is truthy, self.args.columns must be truthy (otherwise the method calls argparser.error and exits).
    - Unless self.args.names_only is truthy, at least one of self.args.regex, self.args.pattern, or self.args.matchfile must be provided (otherwise argparser.error is called and the method exits).
    - self.reader_kwargs and self.writer_kwargs must be dict-like objects; writer_kwargs may optionally contain a boolean 'line_numbers' key.
    - self.output_file must be a writable file-like object suitable for use with agate.csv.writer.
    - get_rows_and_column_names_and_column_ids must return a tuple (rows_iter, column_names, column_ids) consistent with the CSVKitUtility contract.

Postconditions:
    - On successful completion, self.output_file has received a header row (column_names) followed by every row yielded by FilteringCSVReader that matched (or did not match if inverse was True) the provided patterns.
    - If the writer_kwargs originally contained 'line_numbers', that key will no longer exist in self.writer_kwargs after the call, and self.reader_kwargs will include 'line_numbers': True.
    - If a matchfile was supplied via args.matchfile, it will have been closed by this method.
    - The input iterator returned by get_rows_and_column_names_and_column_ids will have been advanced to EOF (or to the iterator's natural stopping point) as rows are consumed during filtering.

## Side Effects:
- Writes to sys.stderr:
    - If additional_input_expected() returns True, writes the message 'No input file or piped data provided. Waiting for standard input:\n' to sys.stderr (this is a visible side effect intended to inform interactive users).

- File I/O:
    - Reads from the input source via the rows iterator produced by get_rows_and_column_names_and_column_ids (this advances the input file read cursor).
    - If args.matchfile is provided, reads all lines from that file (calling rstrip() on each) and closes it.
    - Writes CSV output (header row and data rows) to self.output_file using agate.csv.writer and output.writerow calls.

- Mutations of instance attributes described above (writer_kwargs and reader_kwargs).

- No network or external service calls are performed by this method itself; side effects are limited to file I/O and in-memory mutations.

## `csvkit.utilities.csvgrep.launch_new_instance` · *function*

## Summary:
Instantiate the CSVGrep CLI utility and invoke its run lifecycle, serving as a minimal bootstrap entry point that starts the csvgrep command.

## Description:
- Known callers and typical context:
  - Intended as a module-level entry point that external runners, packaging entry_points (for example, console_scripts), or integration tests import and call to start the csvgrep utility. No internal callers are required; the common usage is at CLI startup time or in tests that exercise the end-to-end CSVGrep.run behavior.
  - Typical trigger: the packaging runner imports this module and calls this function to hand control to the CSVGrep implementation which performs argument parsing and CSV processing.

- Why this logic is extracted into its own function:
  - Provides a stable, importable, and testable entry point to start the csvgrep utility without exposing or requiring knowledge of the CSVGrep class name or internals.
  - Keeps packaging entry_points simple and uniform across utilities by adopting the one-function bootstrap convention.
  - Separates instantiation/bootstrapping concerns from CSVGrep's responsibilities (argument handling, I/O, CSV processing, and filtering).

## Args:
- None. This function accepts no parameters.

## Returns:
- None. The function does not return a value; it returns implicitly if CSVGrep.run completes normally. Any meaningful effects (stdout/stderr output, written files, process exit) are side effects of CSVGrep.run.

## Raises:
- NameError
  - Condition: CSVGrep is not defined or not importable in the module namespace at call time (attempting to call CSVGrep() will raise NameError).
- Any exception raised by CSVGrep.__init__
  - Condition: CSVGrep constructor raises during instantiation; the exception propagates unchanged.
- Any exception raised by CSVGrep.run (including SystemExit)
  - Condition: runtime errors during argument parsing, CSV I/O, filtering, or explicit process termination (e.g., CSVGrep.run calling sys.exit). These exceptions propagate unchanged to the caller.

## Constraints:
- Preconditions:
  - The CSVGrep symbol must be defined and importable in the same module before calling this function.
  - Any runtime context required by CSVGrep.run (for example, command-line arguments in sys.argv, availability of stdin/stdout, or injected framework attributes expected by CSVGrep) should be prepared by the caller; launch_new_instance does not set up runtime context.
- Postconditions:
  - If the function returns normally, CSVGrep.run has completed without raising an exception that escaped to the caller.
  - No value is returned; any CSV output or other side effects have already occurred.

## Side Effects:
- This function itself does no I/O. All side effects originate from CSVGrep.run and may include:
  - Reading CSV input from files or stdin.
  - Writing filtered CSV output to stdout or files.
  - Writing informational messages to stderr (for example, when waiting for stdin).
  - Mutating framework-provided structures used by CSVGrep.run (for example, reader_kwargs and writer_kwargs may be adjusted by CSVGrep.run).
  - Closing any opened matchfile provided via the parsed arguments (CSVGrep.run closes matchfile after building the match set).
  - Raising exceptions or terminating the process (SystemExit) if CSVGrep.run triggers them.

## Control Flow:
flowchart TD
    A[Call launch_new_instance()] --> B[Instantiate CSVGrep()]
    B --> C{CSVGrep.__init__ succeeds?}
    C -- no --> D[Constructor exception propagates (function does not handle it)]
    C -- yes --> E[Call CSVGrep.run()]
    E --> F{CSVGrep.run completes normally?}
    F -- no --> G[Runtime exception or SystemExit propagates]
    F -- yes --> H[Function returns None]

## Examples:
- Programmatic invocation (basic):
    # Start the csvgrep utility (typical packaging entry point usage)
    launch_new_instance()

- Programmatic invocation with error handling:
    try:
        launch_new_instance()
    except NameError:
        # CSVGrep class not available in module namespace
        print("csvgrep entry point not available", file=sys.stderr)
        raise
    except SystemExit:
        # CSVGrep.run may call sys.exit; handle or let it terminate the process
        raise
    except Exception as exc:
        # Handle initialization or runtime errors raised by CSVGrep
        print("csvgrep failed:", exc, file=sys.stderr)
        raise

Notes:
- For details about the behavior, CLI flags, I/O, and specific exceptions that may originate from CSVGrep.run (for example, argument validation errors, regex compilation errors, I/O errors, or filtering errors), consult the CSVGrep component documentation. This function intentionally remains a minimal bootstrap and delegates all command logic to CSVGrep.

