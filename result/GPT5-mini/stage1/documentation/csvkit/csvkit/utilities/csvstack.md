# `csvstack.py`

## `csvkit.utilities.csvstack._skip_lines` · *function*

## Summary:
Advance a file-like object's read position by calling readline() a fixed number of times determined by args.skip_lines, and return the remaining skip counter.

## Description:
This helper reads and discards a specified number of lines from an open file-like object by repeatedly calling its readline() method. It is intended for use by command-line CSV stack/merge logic that needs to ignore header or preliminary lines before processing CSV content. During a repository scan no direct callers were discovered; it is implemented as a small, reusable unit so the skipping logic is centralized (validation of the argument type and the line-consuming loop), keeping higher-level code focused on CSV assembly and error handling.

Why this is a separate function:
- Encapsulates validation that args.skip_lines is an int and the line-skipping loop.
- Makes tests easier (skip behavior can be validated in isolation).
- Keeps the main csvstack logic concise and focused on file handling and data combining.

Known callers:
- None discovered in the provided scan. Expectation: called by csvstack's entry point / main stacking routine when skip_lines behavior is requested.

## Args:
    f (file-like object): An object supporting a readline() method (e.g., an open file, io.StringIO). readline() will be called up to args.skip_lines times. If f does not provide readline, a runtime AttributeError or similar will be raised by the caller of readline().
    args (object): An object with an attribute skip_lines. The function checks that args.skip_lines is an int; typical callers pass an argparse Namespace or a simple object with a numeric attribute.

Notes on allowed values and interdependencies:
- args.skip_lines must be an instance of int. If not, the function raises ValueError with the message 'skip_lines argument must be an int'.
- Negative integers are accepted by the type check but lead to no readline() calls (the function's loop only runs while skip_lines > 0) and the negative value is returned unchanged.
- There is no implicit conversion from other numeric types (e.g., float) or string values.

## Returns:
    int: The final value of the internal skip counter after attempting to skip lines.
    - If args.skip_lines > 0: returns 0 after calling f.readline() exactly args.skip_lines times (regardless of whether EOF was reached during those readline() calls).
    - If args.skip_lines == 0: returns 0 and does not call f.readline().
    - If args.skip_lines < 0: returns the original negative integer unchanged (no calls to f.readline()).
This return value represents the remaining number of lines still to skip (0 when all requested skips were consumed by the loop). The function does not report whether EOF was reached while skipping; it always decrements the counter until zero for positive inputs.

## Raises:
    ValueError: Raised when args.skip_lines is not an instance of int. The raised ValueError uses the message exactly 'skip_lines argument must be an int'.
    AttributeError or other exception: If f does not implement readline(), calling f.readline() will raise (the function does not catch this). Any I/O errors raised by f.readline() propagate to the caller.

## Constraints:
Preconditions:
- args must be an object with a skip_lines attribute.
- f must be file-like and implement readline().

Postconditions:
- For positive initial args.skip_lines, the file object's read position is advanced by calling readline() that many times (each call may read an empty string if EOF is reached); the returned value will be 0.
- For zero or negative initial args.skip_lines, the file's read position is unchanged and the returned value equals the original args.skip_lines.

## Side Effects:
- I/O: Calls f.readline() repeatedly. This will perform reads on the underlying file or buffer and may perform I/O syscalls if f is backed by an OS file descriptor.
- No global state, no network, no stdout/stderr writing, and no mutation of args is performed by this function.

## Control Flow:
flowchart TD
    Start --> CheckType{isinstance(args.skip_lines, int)?}
    CheckType -- No --> RaiseValueError["raise ValueError('skip_lines argument must be an int')"]
    CheckType -- Yes --> AssignSkip["skip_lines = args.skip_lines"]
    AssignSkip --> IsPositive{skip_lines > 0?}
    IsPositive -- No --> ReturnNegZero["return skip_lines (0 or negative)"]
    IsPositive -- Yes --> LoopStart["f.readline(); skip_lines -= 1"]
    LoopStart --> IsPositive
    LoopStart --> ReturnZero["when skip_lines == 0 -> return 0"]

## Examples:
- Example (skip two header lines):
    Context: f is an open CSV file positioned at its start; args.skip_lines is an int = 2.
    Effect: The function calls f.readline() twice (advancing past two lines) and returns 0. After return, the next read from f will start at the third line.

- Example (zero lines requested):
    Context: args.skip_lines == 0.
    Effect: The function does not call f.readline() and returns 0 immediately.

- Example (negative input):
    Context: args.skip_lines == -1.
    Effect: The function checks type, finds an int, does not call f.readline() because the while condition skip_lines > 0 is false, and returns -1 unchanged. Caller should validate that negative skip counts are meaningful before invoking this helper.

- Example (bad type):
    Context: args.skip_lines == "2" (a string).
    Effect: The function raises ValueError with message 'skip_lines argument must be an int'. Caller should catch and handle this if user input may be non-integer.

Implementation note for re-creation:
- Ensure the function performs a strict isinstance(..., int) check and raises the exact ValueError message specified above.
- Use a simple while loop that calls f.readline() and decrements a local skip_lines counter until it reaches zero for positive inputs, then return the local counter.

## `csvkit.utilities.csvstack.CSVStack` · *class*

*No documentation generated.*

### `csvkit.utilities.csvstack.CSVStack.add_arguments` · *method*

## Summary:
Adds four command-line arguments to the instance argument parser so subsequent parsing will accept input file paths and optional grouping controls; this mutates the parser state on the object.

## Description:
This method configures the command-line interface for the CSV stacking utility by registering four arguments on self.argparser. It is intended to be called during CLI setup — typically by a CSVKitUtility subclass or the utility's initialization/run sequence — before arguments are parsed. Keeping argument registration in its own method makes the CLI surface easy to locate, override, or extend in subclasses without inlining parser configuration into higher-level control flow.

Known callers / invocation context:
- Invoked during the CLI argument parser setup phase for the csvstack utility, i.e., when a CSVKitUtility subclass is preparing its argparse.ArgumentParser prior to parse_args().
- Typical lifecycle: instantiate utility -> call method that builds/configures argparser (this method runs) -> parse CLI args -> execute utility logic.

Why separate:
- Argument registration is configuration logic that is orthogonal to parsing and runtime behavior; placing it in its own method makes customization and testing simpler.

## Args:
This method takes only the implicit self parameter; it does not accept additional arguments.

## Behavior / Arguments Added:
The method mutates self.argparser by calling add_argument four times to add these parameters (exact options, destinations, and behaviors as registered):

1. Positional argument:
   - Syntax: FILE
   - Config: metavar='FILE', nargs='*', dest='input_paths', default=['-']
   - Meaning: Zero or more input file paths. If omitted or set to the single value '-', the program should read from STDIN. After parsing, args.input_paths will be a list of strings (file paths), with default ['-'].

2. -g / --groups:
   - Syntax: -g VALUE or --groups VALUE
   - Config: dest='groups'
   - Meaning: A single string expected to be a comma-separated list of grouping values, one per CSV being stacked. The raw parsed value is a string; callers will typically split it on commas to obtain a list.

3. -n / --group-name:
   - Syntax: -n NAME or --group-name NAME
   - Config: dest='group_name'
   - Meaning: A string to use as the name of the grouping column added to stacked output. Only meaningful when -g is also provided (i.e., group_name is used together with groups).

4. --filenames:
   - Syntax: --filenames
   - Config: dest='group_by_filenames', action='store_true'
   - Meaning: Boolean flag. If present, args.group_by_filenames will be True and the filename of each input file should be used as its grouping value. When this flag is used, any value provided to -g/--groups is ignored.

## Returns:
None. The method returns nothing; its effect is to mutate self.argparser by registering new options.

## Raises:
- AttributeError: If self.argparser is not present (missing attribute) or is None, accessing self.argparser or calling add_argument will raise AttributeError.
- Any exceptions raised by the underlying argparse implementation (for instance, errors raised by add_argument if invalid argument parameterization is supplied or if duplicate/conflicting option strings exist). The method itself does not explicitly raise exceptions.

## State Changes:
- Attributes READ:
    - self.argparser (read to call add_argument methods)
- Attributes WRITTEN / Mutated:
    - self.argparser (mutated by registration of four new arguments; the parser's internal state is changed)

## Constraints:
- Preconditions:
    - self must have an attribute argparser that implements an add_argument(name_or_flags..., **kwargs) method (i.e., an argparse.ArgumentParser or similar).
    - The parser should not already have conflicting option strings for the specific flags added (-g, -n, --filenames, and the positional FILE) unless deliberate overrides are acceptable.
- Postconditions:
    - After calling this method, self.argparser will accept:
        * A positional FILE argument (nargs='*'), producing args.input_paths (list[str]) with default ['-'].
        * Optional -g/--groups producing args.groups (str or None).
        * Optional -n/--group-name producing args.group_name (str or None).
        * Optional --filenames producing args.group_by_filenames (bool, False when omitted).
    - If args.group_by_filenames is True at parse time, the value of args.groups (if any) is intended to be ignored by downstream logic (as indicated by the registered help text).

## Side Effects:
- No I/O is performed.
- No network or external service calls.
- The only side effect is mutation of the provided argument parser object (self.argparser). Downstream code that calls parse_args() on that parser will observe the new options.

### `csvkit.utilities.csvstack.CSVStack.main` · *method*

## Summary:
Stacks multiple CSV inputs into a single CSV output stream, optionally adding a grouping column; writes the merged rows (and header) to the command's output file-like object.

## Description:
This method is the CLI entrypoint logic for the csvstack utility. It is invoked when the CSVStack utility is executed (i.e., during the CLI lifecycle when the utility's main/run handler dispatches to this method). It performs two passes over the provided input paths: a first pass to determine combined headers (and to capture stdin-specific fieldnames/first-row data), and a second pass to stream every row from each input into a single output writer while optionally prepending/appending group values.

This logic is separated into its own method because it encapsulates the full end-to-end CSV stacking behavior (argument-driven branching, header discovery, grouping handling, and streaming output). Keeping it as a dedicated method isolates CLI orchestration and I/O flow from lower-level utilities (file opening, line skipping, CSV reader/writer configuration) and makes testing, reuse, and CLI wiring simpler.

Known callers and lifecycle stage:
- Called by the CSVStack utility when executed as a CLI command (the CLI framework that dispatches to the utility will call this method as the primary entrypoint).
- It runs during the runtime/execution phase of the CLI command (after argument parsing and initialization of self.* attributes).

## Args (via self.args and other self attributes accessed):
Note: this method reads configuration from the CSVStack instance (self). The key fields it expects are listed below.

- self.args.input_paths (list[str]): list of input file paths in the order to be stacked. A path equal to '-' denotes standard input.
- self.args.groups (str or None): optional comma-separated string of group values. If provided and group_by_filenames is False, this will be split and applied one-to-one to input_paths.
- self.args.group_by_filenames (bool): if True, derive group values from each input file's basename (f.name).
- self.args.group_name (str or None): optional custom column name for the grouping column; defaults to 'group' when not provided.
- self.args.no_header_row (bool): when True, treat inputs as having no header row (i.e., positional columns) and generate default headers.
- self.reader_kwargs (dict): keyword args forwarded to agate.csv.DictReader or agate.csv.reader when reading CSVs.
- self.writer_kwargs (dict): keyword args forwarded to agate.csv.DictWriter or agate.csv.writer when writing CSVs.
- self.output_file (file-like): writable file-like object where resulting CSV rows are written.
- self.argparser (argparse-like object): used to report fatal argument errors via self.argparser.error(...).
- Other helpers invoked: self._open_input_file(path, opened=False|True) and the module-level helper _skip_lines(fileobj, args).

Defaults / allowed values:
- input_paths must be a non-empty list of file path strings (can include '-').
- groups, if present, must be a comma-separated list of values whose length equals len(input_paths) when group_by_filenames is False.
- group_name defaults to 'group' if not provided.
- no_header_row is a boolean flag.

## Returns:
- None (implicitly). The method writes output through self.output_file rather than returning data.

## Raises:
- Calls self.argparser.error(...) and therefore may terminate the process (typically via SystemExit) when:
    - self.args.groups is provided, group_by_filenames is False, and the number of comma-separated groups does not equal the number of input_paths.
- Errors raised by agate.csv.DictReader / agate.csv.reader (for malformed CSV input) or by file I/O (e.g., FileNotFoundError when opening files via self._open_input_file) may propagate.
- Any exceptions raised by helper functions used (e.g., self._open_input_file, _skip_lines) can propagate.

## Behavior (detailed):
1. If standard input is a TTY and the only input path is '-', writes a prompt message to sys.stderr notifying the user it is waiting for stdin.
2. Determine whether grouping is enabled (has_groups) if either self.args.groups is not None or group_by_filenames is True.
3. If explicit groups string is provided and group_by_filenames is False, split groups by ',' and validate the number of groups equals len(input_paths); on mismatch call self.argparser.error(...).
4. Decide group_name (default 'group') and whether to use fieldnames (use_fieldnames = not no_header_row).
5. Choose Reader:
   - agate.csv.DictReader when use_fieldnames True (reads rows as dicts and exposes .fieldnames).
   - agate.csv.reader when use_fieldnames False (reads rows as sequences/lists).
6. First pass over self.args.input_paths:
   - For each path, open file via self._open_input_file(path) (not forcing pre-opened file).
   - Determine if the path represents stdin via path == '-'.
   - Call _skip_lines(f, self.args) to skip pre-header lines (as configured).
   - Instantiate rows = Reader(f, **self.reader_kwargs).
   - If using fieldnames:
       - Append any new field names encountered in rows.fieldnames to headers in order of discovery.
       - If the file was stdin, record stdin_fieldnames = rows.fieldnames; otherwise close the file.
     Else (no header row):
       - Read the first row via next(rows, []) and generate default headers with make_default_headers(len(row)).
       - If the file was stdin, remember stdin_first_row = row; otherwise close file.
       - Break after the first data file when no headers are present (default headers are determined from the first available row).
7. If grouping enabled, insert group_name at the beginning of headers.
8. Create an agate CSV writer:
   - If use_fieldnames True: instantiate agate.csv.DictWriter(self.output_file, fieldnames=headers, **self.writer_kwargs) and write header row with writeheader().
   - Else: instantiate agate.csv.writer(self.output_file, **self.writer_kwargs) and write a header row as a regular row.
9. Second pass over input_paths (streaming output):
   - For each path (index i):
       - Open file via self._open_input_file(path, opened=True).
       - Determine group value for this file:
           - If has explicit groups (groups list), use groups[i].
           - Else if group_by_filenames True, use os.path.basename(f.name).
       - If not stdin, call _skip_lines(f, self.args).
       - If file is stdin and using fieldnames, set kwargs['fieldnames'] = stdin_fieldnames when constructing the Reader for this file.
       - Instantiate rows = Reader(f, **self.reader_kwargs, **kwargs).
       - If file is stdin and stdin_first_row is non-empty (only applies when no header row), write that saved first row to output before iterating the remaining rows.
       - For each row in rows:
           - If grouping enabled:
               - When using fieldnames (row is a dict): set row[group_name] = group.
               - Otherwise (row is a list): insert group at index 0.
           - Write the row to the output using the CSV writer.
       - Close the input file.
10. End with all input files processed and output written; method returns None.

## State Changes:
Attributes READ:
- self.args (reads input_paths, groups, group_by_filenames, group_name, no_header_row)
- self.reader_kwargs
- self.writer_kwargs
- self.output_file (used as the writer target)
- self.argparser (for error reporting)
- self._open_input_file (helper method invoked)
- Use of module helpers: _skip_lines, make_default_headers

Attributes WRITTEN:
- None of self.* attributes are modified by this method. The method mutates external resources (see Side Effects) but does not assign to instance attributes.

## Preconditions:
- self.args must be present and populated by prior argument parsing.
- self.args.input_paths must be a list of path strings (may include '-').
- self.output_file must be a writable file-like object open for writing.
- self.reader_kwargs and self.writer_kwargs must be dictionaries appropriate for agate.csv reader/writer functions.
- self.argparser should expose an error(msg) method for fatal argument errors.

## Postconditions:
- The output file-like object (self.output_file) has been written with a combined header row followed by rows from each input file, in the same order as self.args.input_paths.
- If grouping was requested, each output row contains a group column under group_name with the appropriate group value.
- All opened input file objects are closed before method completion (the method explicitly calls f.close() for non-stdin files and for files opened in the second pass).
- If a fatal argument validation failed (groups count mismatch), the method calls self.argparser.error(...) and will not produce merged output.

## Side Effects:
- Writes diagnostics to sys.stderr when waiting for stdin on a TTY and no non-stdin inputs were provided.
- May call self.argparser.error(...) which typically terminates the program (SystemExit).
- Opens and closes input files on disk via self._open_input_file.
- Reads data from stdin if '-' is present in input_paths.
- Writes the merged CSV (header + rows) to self.output_file using agate CSV writer APIs.
- Relies on and may propagate exceptions from agate CSV readers/writers and file I/O operations.

## `csvkit.utilities.csvstack.launch_new_instance` · *function*

## Summary:
Create and run a new CSVStack CLI utility instance, handing control to its run() lifecycle and acting as a minimal importable bootstrap entry point that starts the csvstack command.

## Description:
- Known callers and typical context:
    - Packaging entry points (for example console_scripts in package metadata) that start the installed csvstack command at process startup.
    - Integration tests or harnesses that import the module and call this function to run csvstack end-to-end in-process.
    - Any external runner that expects a zero-argument, importable entry point to bootstrap the CSVStack CLI behavior.
    - Typical trigger: the runtime imports the module and calls this function with no arguments when the csvstack command should begin; tests call it to exercise CSVStack.run().

- Why this logic is extracted into its own function:
    - Provides a stable, trivial, and importable entry point for packaging and tests that hides the CSVStack class name and instantiation details.
    - Keeps bootstrapping separate from CSVStack implementation so callers can start the CLI behavior with a single, consistent call.
    - Ensures a uniform convention across csvkit utilities (many sibling modules expose the same one-line launch_new_instance wrapper), simplifying packaging configuration and test harness code.

## Args:
- None.

## Returns:
- None.
    - The function returns implicitly (None) when CSVStack.run() completes normally.
    - If CSVStack.run() blocks (for example an interactive mode), this function will block until run() returns or raises.
    - If CSVStack.__init__ or CSVStack.run() raises, that exception propagates and the function does not return normally.

## Raises:
- NameError
    - Condition: CSVStack is not defined in the module namespace when attempting to instantiate it (CSVStack()).
- Any exception raised by CSVStack.__init__
    - Condition: constructor-time errors during instantiation (these propagate unchanged).
- Any exception raised by CSVStack.run()
    - Condition: runtime failures during argument parsing, I/O, CSV processing, interactive sessions, or explicit process termination (for example SystemExit). These propagate unchanged.

## Constraints:
- Preconditions:
    - The CSVStack symbol must be defined and constructable in the module namespace at call time.
    - Any runtime context CSVStack.run() expects (for example sys.argv contents, input files or streams) should be prepared by the caller; this wrapper does not set up command-line arguments or environment.
- Postconditions:
    - On normal return, CSVStack.run() has finished its lifecycle and any side effects performed by it (loading CSVs, writing output, launching an interactive REPL, printing to stdout/stderr, mutating global config) have already occurred.
    - No value is returned to indicate success; callers must infer outcome from the absence of exceptions or from side effects.

## Side Effects:
- This wrapper performs no direct I/O other than constructing an object and calling its method.
- All observable side effects originate from CSVStack.run(), and may include:
    - Reading CSV input (files or stdin) and creating in-memory representations (e.g., agate tables).
    - Writing CSV output to stdout or files.
    - Launching an interactive REPL that blocks the process until exit.
    - Printing welcome/diagnostic messages to stdout/stderr.
    - Mutating global configuration used by agate or the CLI framework.
    - Raising SystemExit or other exceptions that propagate to the caller.

## Control Flow:
flowchart TD
    A[Call launch_new_instance()] --> B[Instantiate CSVStack()]
    B --> C{CSVStack.__init__ succeeds?}
    C -- no --> D[Constructor exception propagates to caller]
    C -- yes --> E[Call CSVStack.run()]
    E --> F{CSVStack.run() completes normally?}
    F -- yes --> G[Function returns None]
    F -- no --> H[Runtime exception or SystemExit propagates to caller]

## Examples:
- Packaging usage (conceptual):
    - Register csvkit.utilities.csvstack:launch_new_instance as a console_scripts entry point so the packaging/runtime imports the module and calls launch_new_instance() to start the installed "csvstack" command.

- Programmatic invocation with error handling:
    - Typical pattern for tests or harnesses that want to run the utility but handle expected failures:
        try:
            launch_new_instance()
        except NameError:
            # CSVStack class not available in this runtime/module
            handle_missing_entry_point()
        except SystemExit as se:
            # Argument parser or explicit exit occurred in CSVStack.run()
            handle_exit_condition(se)
        except Exception as exc:
            # Other runtime errors from CSVStack.run() (I/O, parsing, etc.)
            handle_runtime_error(exc)

