# `csvclean.py`

## `csvkit.utilities.csvclean.CSVClean` · *class*

*No documentation generated.*

### `csvkit.utilities.csvclean.CSVClean.add_arguments` · *method*

## Summary:
Registers a command-line flag that toggles "dry run" behavior by mutating the instance's argument parser state so the utility can detect when output files should not be written.

## Description:
This method adds a boolean (store_true) command-line option to the object's argument parser that indicates the utility should run in dry-run mode. The main() method of the same class examines the parsed arguments (self.args.dryrun) to decide whether to write output files or only report what would have been done; therefore this logic is separated into its own method to keep CLI option registration distinct from runtime behavior.

Known callers and lifecycle context:
- Intended to be invoked during CLI setup by the CSVKit utility framework prior to parsing command-line arguments. In this class, main() relies on the option that this method registers (self.args.dryrun) to select dry-run behavior.

Why this is a separate method:
- Keeps command-line interface configuration (argument registration) decoupled from runtime logic (main), following the pattern used by CSVKit utilities where each utility registers its own options in add_arguments().

## Args:
This method takes no external arguments (only self).

## Returns:
None. The method returns no value and its effect is only the mutation of the argument parser state.

## Raises:
- AttributeError: if self.argparser is missing or does not expose an add_argument method, an AttributeError will be raised when attempting to call self.argparser.add_argument.
- Any exceptions raised by the underlying argument parser implementation when registering an option (for example, if the same option is already registered in an incompatible way). These propagate directly from the parser's add_argument implementation.

## State Changes:
Attributes READ:
- self.argparser

Attributes WRITTEN / Mutated:
- self.argparser (the parser's internal configuration is modified by calling add_argument; new action/option for '-n'/'--dry-run' is registered)

## Constraints:
Preconditions:
- self must have an attribute argparser that is an argument parser-like object exposing an add_argument(name_or_flags..., **kwargs) method (for example, argparse.ArgumentParser or compatible wrapper).
- The argument names '-n' and '--dry-run' must be valid for the parser (i.e., not conflict in an unrecoverable way with previously registered options).

Postconditions:
- After successful execution, the argument parser is configured to accept '-n' or '--dry-run'. When parsing arguments later, the parser will set the destination attribute 'dryrun' on the parsed args object to True if the option is present, otherwise False.
- No return value; only the parser's registration changes are guaranteed.

## Side Effects:
- Mutates the argument parser object's internal registration of options (no file I/O or network I/O).
- No writes to disk, no stdout/stderr writes, and no modification of other object attributes besides the parser's configuration.
- If the parser's add_argument raises, that exception will propagate to the caller.

## Registered option details (explicit):
- Flags: -n, --dry-run
- dest: 'dryrun'
- action: 'store_true' (boolean flag; True when present)
- help text: "Do not create output files. Information about what would have been done will be printed to STDERR."

### `csvkit.utilities.csvclean.CSVClean.main` · *method*

## Summary:
Orchestrates the csvclean CLI action: reads input (after skipping configured lines), runs RowChecker to detect and fix common CSV problems, and either reports findings (dry run) or writes a cleaned CSV and an error CSV while emitting status messages to the configured output stream.

## Description:
This is the main entrypoint for the csvclean utility. Typical callers and lifecycle:
- Invoked by the CLI command dispatch after argument parsing and initialization of the CSVClean instance (i.e., as the primary action when a user runs the csvclean command).
- It runs during the command's execution stage: it prepares an input reader, runs validation/cleaning logic, and produces output (files and/or status messages).

Why this logic is its own method:
- It encapsulates the end-to-end orchestration of input preparation, RowChecker invocation, and output production. Keeping this orchestration in a dedicated main method simplifies the CLI dispatcher's job and isolates side-effectful operations (file I/O and message reporting) from lower-level helpers (skip_lines, RowChecker, _format_error_row).

## Args:
None. This is an instance method and relies entirely on attributes of self.

## Returns:
None (implicitly returns None). All results are produced via side effects: files on disk and writes to self.output_file.

## Raises:
- ValueError: may be raised by self.skip_lines() if self.args.skip_lines is not an int (see CSVKitUtility.skip_lines for exact condition and message).
- AttributeError: may be raised if expected attributes are missing on self (for example, if self.args, self.input_file, or self.output_file are not present); additional_input_expected() may also raise AttributeError if self.args lacks input_path.
- OSError (or subclasses, e.g., IOError on older Python): may be raised when opening or writing to output files (e.g., permission denied, directory not writable).
- Any exception raised by agate.csv.reader, RowChecker construction, checked_rows iteration, or the CSV writer invoked in this method will propagate. These include parsing errors, TypeError if reader/writer kwargs are invalid, or exceptions raised while iterating the input.

Notes:
- The method does not explicitly raise these exceptions itself; they come from called helpers or I/O operations. Callers should be prepared to handle or report these errors.

## State Changes:
Attributes READ:
- self.args (inspected for dryrun and used indirectly by skip_lines)
- self.args.dryrun (checked to select dry-run vs write mode)
- self.args.skip_lines (read and then mutated by skip_lines; see WRITTEN)
- self.args.input_path (read indirectly by additional_input_expected())
- self.input_file (the file-like object used as input; its .name may be read)
- self.output_file (file-like object to which status messages are written)
- self.reader_kwargs (mapping forwarded to agate.csv.reader)
- self.writer_kwargs (mapping forwarded to agate.csv.writer)
- self._format_error_row (method used to format error rows)
- methods: self.additional_input_expected(), self.skip_lines()

Attributes WRITTEN:
- self.args.skip_lines: may be decremented to 0 by the call to self.skip_lines() (see CSVKitUtility.skip_lines for behavior).
- No other attributes on self are modified by this method.

## Constraints:
Preconditions (what must be true before calling):
- The CSVClean instance must have:
    - self.args with at least attributes dryrun (bool) and skip_lines (int). If skip_lines is not an int, skip_lines() will raise ValueError.
    - self.input_file: a readable file-like object with a readline() method and, if non-stdin, a .name attribute used to derive output filenames.
    - self.output_file: a writable file-like object with a write() method (used to emit status messages and dry-run output).
    - self.reader_kwargs and self.writer_kwargs: dictionaries valid for agate.csv.reader and agate.csv.writer respectively.
- The environment must allow creation/writing of files in the current working directory when not running in dry-run mode.

Postconditions (what is guaranteed after calling):
- If args.dryrun is True:
    - No output files with suffixes _out.csv or _err.csv are created by this method.
    - self.output_file will have received either a "No errors.\n" message or lines describing each error ("Line N: message\n"), and possibly a message describing the number of rows that would have been joined/reduced.
    - self.args.skip_lines will have been consumed/decremented as skip_lines() defines.
- If args.dryrun is False:
    - A cleaned CSV file named "<base>_out.csv" will be created (where base is derived from self.input_file.name or set to 'stdin' when input_file is sys.stdin); it will contain a header row (checker.column_names) followed by the cleaned rows returned by RowChecker.checked_rows().
    - If RowChecker.errors is non-empty, an error CSV "<base>_err.csv" will be created containing a header ['line_number','msg', ...column names...] and one row per error as formatted by self._format_error_row(error). A status message describing the number of errors and the error filename will be written to self.output_file.
    - If RowChecker.errors is empty, a "No errors.\n" message will be written to self.output_file.
    - If RowChecker.joins is truthy, a message describing how many rows were joined/reduced will be written to self.output_file.
    - self.args.skip_lines will have been consumed/decremented as skip_lines() defines.

## Behavior and Key Steps (detailed):
1. If additional input is expected (self.additional_input_expected() returns truthy), write a prompt-like message to sys.stderr noting that standard input is awaited.
2. Create a CSV reader using agate.csv.reader, passing the file-like object returned by self.skip_lines() (which advances the input by self.args.skip_lines lines) and the stored self.reader_kwargs.
3. If running in dry-run mode (self.args.dryrun is truthy):
    - Instantiate RowChecker with the reader.
    - Iterate through checker.checked_rows() to force the RowChecker to validate the entire input (rows are not written anywhere in dry run).
    - If checker.errors is non-empty, write one human-readable line per error to self.output_file in the form "Line <n>: <message>\n".
    - Otherwise write "No errors.\n" to self.output_file.
    - If checker.joins is truthy, write a summary line stating how many rows would have been joined/reduced and to how many rows after eliminating expected internal line breaks.
4. If not in dry-run mode:
    - Determine base filename:
        - If self.input_file is sys.stdin, base is the literal string 'stdin' (avoids producing "<stdin>_out.csv" which is invalid on Windows).
        - Otherwise base is splitext(self.input_file.name)[0].
    - Open "<base>_out.csv" for writing and construct an agate.csv.writer with self.writer_kwargs.
    - Instantiate RowChecker with the reader.
    - Write checker.column_names as the header row to the output CSV.
    - Iterate checker.checked_rows() and write each returned row to the cleaned output CSV.
    - After writing the cleaned CSV:
        - If checker.errors exists:
            - Create "<base>_err.csv" and write an error header composed of ['line_number', 'msg'] extended with checker.column_names.
            - Write one formatted error row per error using self._format_error_row(error).
            - Write a status line to self.output_file describing how many errors were logged and the filename.
        - If no errors, write "No errors.\n" to self.output_file.
        - If checker.joins is truthy, write a summary line describing how many rows were joined/reduced.

## Edge Cases and Notes:
- Input-from-stdin naming: When reading from sys.stdin the method uses base='stdin' to avoid using sys.stdin's repr or invalid filename components; this ensures output filenames are valid on Windows.
- Entire input may be consumed: RowChecker.checked_rows() is iterated to completion in both dry-run and normal modes, so the input stream will be read fully by this call.
- skip_lines interaction: Because this method calls self.skip_lines(), if args.skip_lines is positive, it will be decremented to 0 by that helper and the underlying input_file read pointer will be advanced accordingly.
- Error object expectations: This method assumes each error object yielded by RowChecker.errors exposes at least the attributes:
    - line_number (int)
    - msg (str)
    - row (sequence): the original row data used by _format_error_row
  These attributes are used when writing human-readable messages and when composing the error CSV rows.
- Output encoding and dialect: agate.csv.writer is used with self.writer_kwargs; ensure those kwargs supply any necessary dialect or encoding to match input expectations.
- When writer/reader kwargs are invalid or missing required parameters for the agate CSV utilities, underlying TypeError/ValueError/CSV parsing exceptions may be raised.

## Side Effects:
- File system:
    - In non-dry-run mode, creates/writes "<base>_out.csv" and, when errors exist, "<base>_err.csv" in the current working directory (or raises OSError on failure).
- Standard streams:
    - Writes prompt text to sys.stderr if additional input is expected.
    - Writes status and error summary lines to self.output_file (which may be sys.stdout or a different file-like object).
- Input stream:
    - Reads from self.input_file (after skipping configured lines); the stream's read position is advanced and typically consumed entirely.
- External objects:
    - Instantiates RowChecker and iterates its checked_rows(), which may perform parsing/validation and internal memory allocations; any side effects of RowChecker (e.g., internal counters) occur independently of CSVClean state.

### `csvkit.utilities.csvclean.CSVClean._format_error_row` · *method*

## Summary:
Convert a RowChecker error object into a flat list suitable for writing as a CSV error row; does not modify the CSVClean instance.

## Description:
Known callers and context:
- Called from CSVClean.main in the non-dry-run path when writing an error CSV file. Specifically, each error object e from checker.errors is passed to this method and the returned list is written via error_writer.writerow(self._format_error_row(e)).
- Invocation occurs after RowChecker has finished checking rows (after checker.checked_rows() iteration), as part of the pipeline step that persists detected errors to an error output CSV.

Why this is a separate method:
- Isolates the logic that maps an error object to the exact CSV row layout (line number, message, then original row values), making the formatting easy to maintain, test, and reuse. Separating formatting avoids duplicating the list construction at the write site and clarifies the intended column ordering for the error file.

## Args:
    error (object): An error record produced by RowChecker or equivalent with the following attributes:
        - line_number (int): 1-based source line number where the error was detected.
        - msg (str): Human-readable error message describing the problem.
        - row (iterable): The original row values (list/tuple) associated with the error.
    No default; positional argument required.

## Returns:
    list: A list whose first element is error.line_number (int), second element is error.msg (str), and whose remaining elements are the items from error.row in order.
    - Possible values: When error.row is empty, the returned list has only the line number and message. If error.row contains non-string values, they are included as-is (the CSV writer will convert them when writing).
    - Edge cases: If error.row is an iterator that can be exhausted, the returned list will contain whatever values remain at the time of the call.

## Raises:
    AttributeError: If the provided error object does not expose the required attributes (line_number, msg, or row).
    Any exception raised while iterating error.row (for example, if row is a generator that raises) will propagate to the caller.

## State Changes:
    Attributes READ:
        - None on self (this method does not access self.<attr>).
        - Reads attributes from the error argument: error.line_number, error.msg, error.row.
    Attributes WRITTEN:
        - None on self (no modifications to the CSVClean instance).

## Constraints:
    Preconditions:
        - The caller must supply an object with attributes line_number (int-like), msg (str-like), and row (iterable).
        - If error.row is an iterator, it should be safe to iterate at call time (i.e., not already exhausted if its contents are needed).
    Postconditions:
        - Returns a list with the specified ordering: [line_number, msg, *row_values].
        - Does not mutate the error object or the CSVClean instance.

## Side Effects:
    - No I/O performed by this method.
    - No external service calls.
    - No mutations of objects outside of the local return value, except that iterating over error.row may advance/consume the provided iterable if it is not a concrete sequence.

## `csvkit.utilities.csvclean.launch_new_instance` · *function*

## Summary:
Creates a new CSVClean command-line utility instance and executes it; intended to serve as the simple entry point that boots the CSVClean utility and runs its CLI behavior.

## Description:
This function performs the minimal bootstrap for the CSVClean utility by constructing a CSVClean object and invoking its run method. Within this codebase, several sibling modules expose identical small entry functions (for example csvkit.utilities.csvsort.launch_new_instance, csvkit.utilities.csvcut.launch_new_instance, and others) which follow the same pattern; this establishes the convention that a module-level launch_new_instance function acts as a small adapter to create and run the utility instance.

Known callers within the repository:
- No direct internal callers were found in the code graph for this function. The typical use case is that this function is referenced externally (for example, as a packaging/console_scripts entry point or invoked by a CLI runner) to start the CSVClean utility.

Why this logic is extracted:
- Responsibility separation: extracting instantiation and execution into a one-line function provides a stable, importable entry point that external runners (packaging entry points, integration tests, or other CLI orchestration code) can call without needing to know the internal class name.
- Keeps packaging and entry-point code simple and uniform across utilities: other utility modules expose the same single-function entry point making it trivial to wire into console entry_points.

## Args:
This function accepts no arguments.

## Returns:
None.
- The function's return value is implicitly None because it does not return anything.
- Any meaningful result or exit behavior is produced by CSVClean.run (for example printing to stdout or exiting the process); those outcomes are not returned by this function.

## Raises:
- Any exception raised by CSVClean.__init__ (constructor) will be propagated unchanged.
- Any exception raised by CSVClean.run will be propagated unchanged.
- If CSVClean is not defined or not importable in the module namespace, a NameError will be raised at runtime when attempting to instantiate it.

## Constraints:
Preconditions:
- The CSVClean class must be defined and importable in the same module or reachable namespace before this function is called.
- Any runtime resources required by CSVClean.run (such as access to sys.argv, input files, or environment variables) must be in the expected state; this function does not validate those conditions itself.

Postconditions:
- After a successful call, the CSVClean.run method has executed to completion. There is no guaranteed returned value from this function.
- Any side effects performed by CSVClean.run (file writes, stdout output, process exit, etc.) will have occurred.

## Side Effects:
- Indirect I/O and external effects depend entirely on CSVClean.run. Typical side effects for a CLI utility's run method may include:
    - Reading input CSV files and writing cleaned output (files or stdout).
    - Writing to stdout and stderr.
    - Exiting the process (e.g., by calling sys.exit) — such an exit call will terminate the Python process running this function.
    - Logging or printing status and error messages.
- This function itself performs no I/O beyond delegating to CSVClean.run; any external state changes are the responsibility of the CSVClean implementation.

## Control Flow:
flowchart TD
    A[Call launch_new_instance()] --> B[Instantiate CSVClean()]
    B --> C{CSVClean.__init__ succeeds?}
    C -- no --> D[Exception propagates from constructor]
    C -- yes --> E[Call CSVClean.run()]
    E --> F{CSVClean.run completes normally?}
    F -- no --> G[Exception propagates from run]
    F -- yes --> H[launch_new_instance returns None]

## Examples:
- Basic invocation from Python (delegates to the utility's run method):
    try:
        launch_new_instance()
    except Exception as e:
        # Handle initialization or runtime errors from the CSVClean utility
        print("CSVClean failed:", e, file=sys.stderr)
        raise

- Typical packaging usage (conceptual):
    # In package metadata (not shown here), this function is often registered as a
    # console_scripts entry point so that executing the installed command starts
    # CSVClean. The packaging system invokes this function with no arguments.
    # e.g., "csvclean = csvkit.utilities.csvclean:launch_new_instance"
    pass

