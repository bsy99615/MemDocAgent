# `csvsort.py`

## `csvkit.utilities.csvsort.CSVSort` · *class*

## Summary:
A CSV command utility that registers CLI options and implements the runtime to read a CSV, sort its rows by user-specified column selector(s) (names, numeric indices, or ranges), and write the sorted CSV to the configured output.

## Description:
CSVSort is the csvsort CLI command implementation. It separates two concerns:
- CLI declaration (add_arguments): registers flags used by the command-line interface. Note: add_arguments only defines option names, destinations, types, defaults, and help text; it does not parse arguments or perform runtime behavior.
- Execution orchestration (main): validates input, reads a CSV via agate, resolves column selectors via parse_column_identifiers, sorts rows with agate.Table.order_by, and writes results using table.to_csv.

This class is intended to be constructed and invoked by the csvkit CLI dispatcher (CSVKitUtility runner). It delegates CSV parsing/writing and detailed column-selector parsing to collaborators (agate and parse_column_identifiers) rather than reimplementing those concerns.

Class attribute:
- description (str): "Sort CSV files. Like the Unix \"sort\" command, but for tabular data." — used by the CLI help text.

When to use:
- When building or testing the csvsort command-line tool, or when embedding csvsort-style functionality into a CLI flow that uses CSVKitUtility-compatible runners.

Why it exists:
- To provide an end-to-end, consistent CLI command that turns user column selectors into a sorted CSV output while leveraging agate for parsing/sorting and a shared parser for selector semantics.

## Public Methods and Signatures:
- add_arguments(self) -> None
  - Registers five CLI options on self.argparser. No parameters; side-effect: mutates self.argparser. It only declares options — it does not parse or act on them.

- main(self) -> None
  - Executes the utility's operation using state populated on the instance (self.args, self.input_file, self.output_file, reader_kwargs, writer_kwargs, and helper methods provided by the base class).
  - Returns None. Performs I/O and may terminate the process via argparser.error(...).

## State (attributes relied upon):
These attributes are expected to be present (supplied by CSVKitUtility/runner). CSVSort reads them; it does not define them.

- argparser
  - Type: argparse.ArgumentParser-like object
  - Must implement: add_argument(...) and error(msg)
  - Used by add_arguments to register CLI flags and by main to report missing-input errors.

- args
  - Type: namespace-like object populated by argparser.parse_args()
  - Required attributes (read by main):
    - names_only: bool (flag -n/--names)
    - columns: str | None (flag -c/--columns)
    - reverse: bool (flag -r/--reverse)
    - sniff_limit: int (flag -y/--snifflimit), default 1024
    - no_inference: bool (flag -I/--no-inference)
    - skip_lines: int (number of leading lines to skip; used by agate.Table.from_csv)
  - Constraint: must be set before calling main. Parsing of CLI arguments is performed by the caller/runner; add_arguments only registers the options.

- input_file
  - Type: file path string or readable file-like object accepted by agate.Table.from_csv
  - Constraint: must be readable unless names-only path is used and print_column_names can handle input.

- output_file
  - Type: file path string or writable file-like object accepted by agate.Table.to_csv
  - Constraint: must be writable when main writes output.

- reader_kwargs, writer_kwargs
  - Type: dict
  - Purpose: forwarded to agate.Table.from_csv / table.to_csv

- Helper methods (must exist on the instance):
  - get_column_types() -> dict | None
    - Purpose: supply column type mapping for agate.Table.from_csv. CSVSort itself does not implement the --no-inference behavior; the get_column_types implementation should consult args.no_inference if the runner requires disabling type inference.
  - get_column_offset() -> int
    - Purpose: integer offset supplied to parse_column_identifiers to interpret numeric selectors (commonly 1 for 1-based user input).
  - additional_input_expected() -> bool
    - Purpose: returns True if missing input should cause a usage error.
  - print_column_names() -> None
    - Purpose: prints header names and indices to output and returns. When args.names_only is True (after the caller has parsed arguments), main will call this helper.

## Behavior: Exact runtime flow (main)
1. Names-only short-circuit:
   - After the caller has parsed CLI arguments into self.args, if self.args.names_only is truthy:
     - main calls self.print_column_names() and immediately returns. add_arguments only declares the flag; the runtime behavior is implemented here.

2. Input availability check:
   - If self.additional_input_expected() returns True:
     - Call self.argparser.error('You must provide an input file or piped data.')
     - This call typically raises SystemExit (argparse behavior); implementers should expect process termination.

3. Determine sniff_limit passed to agate:
   - If self.args.sniff_limit == -1 -> set sniff_limit = None (meaning "sniff entire stream" for agate).
   - Otherwise set sniff_limit = self.args.sniff_limit (including 0 meaning "disable sniffing").

4. Prepare column type hints:
   - Call column_types = self.get_column_types() and pass this value to agate.Table.from_csv. The handling of args.no_inference is the responsibility of get_column_types; add_arguments only registered the flag.

5. Read CSV into agate.Table:
   - Call agate.Table.from_csv(
       self.input_file,
       skip_lines=self.args.skip_lines,
       sniff_limit=sniff_limit,
       column_types=column_types,
       **self.reader_kwargs
     )
   - Capture the returned agate.Table in variable table. Propagate any exceptions raised by agate (I/O or parse errors).

6. Resolve column selectors:
   - Call column_ids = parse_column_identifiers(
       self.args.columns,
       table.column_names,
       self.get_column_offset()
     )
   - Important: parse_column_identifiers may return either:
     - range(len(table.column_names)) when args.columns is falsy and excluded_columns is falsy (early-return optimization), or
     - list[int] of 0-based indices otherwise.
   - CSVSort passes column_ids directly to agate.Table.order_by; ensure your implementation accepts both.

7. Sort table:
   - Call table = table.order_by(column_ids, reverse=self.args.reverse)

8. Write CSV output:
   - Call table.to_csv(self.output_file, **self.writer_kwargs)

9. Return:
   - main returns None on normal completion.

## Edge cases and constraints (explicit):
- Column selector parsing:
  - args.columns may be None or empty; parse_column_identifiers handles the default-to-all-columns case and may return a range object. Do not assume a concrete list without checking compatibility with agate.order_by.
  - Numeric selectors are interpreted using get_column_offset() (commonly 1 for human-friendly 1-based indices).
  - Malformed selectors or invalid indices will cause parse_column_identifiers to raise ColumnIdentifierError (propagated by main).

- Sniffing behavior:
  - args.sniff_limit defaults to 1024. A value of 0 disables sniffing. A value of -1 instructs CSVSort to pass sniff_limit=None to agate, meaning the entire stream should be sniffed.

- No-inference:
  - add_arguments registers the --no-inference flag only; CSVSort delegates type inference handling to get_column_types(). The runner or get_column_types implementation should consult args.no_inference to disable inference if required.

- Resource management:
  - CSVSort itself does not open or close files. If the runner provides open file-like objects for input_file/output_file, the runner (caller) is responsible for closing them.

## Exceptions and raises (precise):
add_arguments:
- AttributeError if self.argparser is missing or does not implement add_argument.
- Errors from the underlying parser.add_argument (TypeError/ValueError) propagate if invalid parameters are supplied.

main:
- SystemExit: when self.argparser.error(...) is called due to missing input (typical argparse behavior).
- Any exception from agate.Table.from_csv(...) (FileNotFoundError, CSV parsing errors, agate-specific errors).
- ColumnIdentifierError (or other exceptions) from parse_column_identifiers(...) when selectors are invalid or ranges malformed.
- Exceptions from agate.Table.order_by or table.to_csv (I/O exceptions like PermissionError, BrokenPipeError).
- Exceptions raised by helper methods (get_column_types, get_column_offset, additional_input_expected, print_column_names) if those implementations raise.

## Reimplementation checklist (step-by-step, exact actions to reproduce behavior):
1. Ensure instance exposes argparser, args, input_file, output_file, reader_kwargs, writer_kwargs, and helper methods listed above.
2. Implement add_arguments:
   - Call argparser.add_argument with these exact flag sets:
     - '-n', '--names'      -> dest='names_only', action='store_true', help='Display column names and indices from the input CSV and exit.'
     - '-c', '--columns'    -> dest='columns', help='A comma-separated list of column indices, names or ranges to sort by, e.g. "1,id,3-5". Defaults to all columns.'
     - '-r', '--reverse'    -> dest='reverse', action='store_true', help='Sort in descending order.'
     - '-y', '--snifflimit' -> dest='sniff_limit', type=int, default=1024, help='Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely, or "-1" to sniff the entire file.'
     - '-I', '--no-inference' -> dest='no_inference', action='store_true', help='Disable type inference when parsing the input.'
   - Do not parse arguments or implement runtime behavior here; add_arguments only registers flags.
3. Implement main to follow the exact flow outlined in "Behavior" above, respecting sniff_limit mapping and delegating column type handling to get_column_types().
4. When calling parse_column_identifiers, pass table.column_names and self.get_column_offset(); accept a range or list as the result.
5. Do not close file-like objects inside main; leave resource cleanup to the caller.
6. Propagate exceptions from agate and parse_column_identifiers; do not swallow or translate them (except for the intended argparser.error path).

## Examples / Scenarios (concrete, textual):
- Names-only:
  - CLI: csvsort --names input.csv
  - Behavior: add_arguments has registered --names / -n; after the CLI runner parses arguments into self.args, if args.names_only is True then main calls print_column_names() and returns without sorting.

- Missing input:
  - If the runner did not supply an input_file and additional_input_expected() returns True:
  - Behavior: main calls argparser.error('You must provide an input file or piped data.'), typically causing SystemExit and a non-zero exit code.

- Sorting by name and numeric range:
  - CLI: csvsort -c "id,2-4" input.csv > out.csv
  - Behavior: parse_column_identifiers resolves "id,2-4" into 0-based indices using table.column_names and get_column_offset(); table.order_by sorts by those indices; result is written to stdout (redirected to out.csv).

- Disable type inference:
  - CLI: csvsort -I input.csv
  - Behavior: add_arguments registers --no-inference; CSVSort calls get_column_types() and the runner/get_column_types implementation should ensure that args.no_inference results in column_types that prevent agate from performing type inference.

## Why this documentation is sufficient to reimplement CSVSort:
- It lists exact CLI flags and destinations, precise main control flow, the exact mapping of sniff_limit special values, how to call parse_column_identifiers (and what return types to expect), and the sequence of agate calls required. The checklist provides an ordered set of implementation steps that, together with agate and parse_column_identifiers, allow faithful reconstruction of CSVSort's behavior.

### `csvkit.utilities.csvsort.CSVSort.add_arguments` · *method*

## Summary:
Registers five command-line options on the object's argument parser to control column listing, column selection for sorting, sort direction, CSV dialect sniffing limits, and type inference; this mutates self.argparser so the CLI will produce the corresponding parsed attributes.

## Description:
This method declares the CSV sort utility's CLI flags by calling add_argument on self.argparser five times. It does not parse arguments or implement sort logic; it only defines the flags, their destination names, value types, defaults, and help text. The resulting dest names are intended to be read later after argument parsing (for example, by the utility's run/execute method).

Why this is a separate method:
- Keeps CLI option registration localized to the CSVSort utility.
- Separates parser configuration from parsing and business logic, making it easier to test and to reuse the same parser setup pattern across utilities.

Known downstream consumer/context:
- The flags registered here produce attributes on the parsed args namespace (e.g., args.names_only, args.columns, etc.). The columns string registered by the --columns option is expected to be parsed into concrete column identifiers later (the module imports parse_column_identifiers for that purpose), so this method deliberately does not validate or transform the columns value.

## CLI Options Registered (exact flags and destinations):
- -n, --names
  - dest: names_only
  - type: boolean flag via action='store_true'
  - default: False (implicit)
  - Effect: When True, the utility should display column names and indices and exit.

- -c, --columns
  - dest: columns
  - type: str (no explicit type set; argparse yields a string)
  - default: None (implicit)
  - Effect: Comma-separated list of column indices, names or ranges (example form: "1,id,3-5"). If None or omitted, the caller should treat this as "all columns".

- -r, --reverse
  - dest: reverse
  - type: boolean flag via action='store_true'
  - default: False (implicit)
  - Effect: When True, sorting should be performed in descending order.

- -y, --snifflimit
  - dest: sniff_limit
  - type: int
  - default: 1024
  - Effect: Controls CSV dialect sniffing:
      * >0: number of bytes to read for sniffing
      * 0: disable sniffing
      * -1: sniff the entire stream

- -I, --no-inference
  - dest: no_inference
  - type: boolean flag via action='store_true'
  - default: False (implicit)
  - Effect: When True, callers should disable type inference and treat fields as raw strings.

## Args:
This method takes only self; no additional parameters.

## Returns:
None. The method's purpose is side-effecting: registering options on self.argparser.

## Raises:
The method body does not explicitly raise exceptions. Possible runtime exceptions that may propagate:
- AttributeError: if self.argparser is None or does not implement add_argument.
- TypeError/ValueError: if the parser implementation's add_argument rejects provided parameters.

## State Changes:
Attributes READ:
- self.argparser (used to call add_argument)

Attributes WRITTEN:
- self.argparser (its internal option registry is modified by repeated add_argument calls; the attribute reference itself is not replaced)

No other attributes of self are read or modified.

## Constraints:
Preconditions:
- self.argparser must be an object exposing add_argument and accepting the keyword parameters used (flags list, dest, action, type, default, help).

Postconditions:
- self.argparser will have option definitions for dest names: names_only, columns, reverse, sniff_limit, no_inference.
- After argument parsing, the parsed namespace will include:
    * args.names_only -> bool
    * args.columns -> str or None
    * args.reverse -> bool
    * args.sniff_limit -> int (default 1024 unless overridden)
    * args.no_inference -> bool

## Side Effects:
- Mutates the internal configuration/state of self.argparser by registering five CLI options.
- No I/O, network calls, or mutations to objects outside self.argparser are performed by this method.

## Implementation Checklist (to reimplement exactly):
- For each option, call self.argparser.add_argument with the same short and long flags, the same dest name, and the same action/type/default as described above.
- Boolean flags must use action='store_true' to yield False by default and True when specified.
- Set sniff_limit with type=int and default=1024.
- Do not parse or validate the columns string here; leave parsing to the later processing stage (e.g., code that uses parse_column_identifiers).
- Do not return a value; ensure the method only registers arguments.

### `csvkit.utilities.csvsort.CSVSort.main` · *method*

## Summary:
Execute the csvsort utility's main runtime: read input CSV data (file or stdin), determine sort column(s), perform the sort using agate, and write the sorted CSV to the configured output (file or stdout). Does not return a value; drives I/O and process control for the utility.

## Description:
This method is the primary entry point for the CSV sorting command-line utility. It implements the high-level flow for the command:
- Optionally print column names and exit when the user requested names-only output.
- Ensure input is provided (file or piped data) and report an error if missing.
- Load the input into an agate.Table with configured sniffing, skipping, and column type hints.
- Resolve user column identifiers (names or indices) into column indices using the loaded table and any configured offset.
- Sort the table by the resolved column indices (optionally in reverse order).
- Write the sorted table to the configured output destination.

Known callers and invocation context:
- Invoked as the CLI command entrypoint for the csvsort utility during normal command-line execution. In the csvkit utilities design, an instance of this utility class is created and this main method is called as part of the CLI dispatch/run lifecycle (i.e., when the user runs the csvsort command).
- Lifecycle stage: called after argument parsing and utility object construction, and before process termination; it is responsible for performing the operation requested by the parsed arguments.

Why this is a separate method:
- Encapsulates the end-to-end behavior of the command-line operation (argument-driven control flow, I/O, table construction, validation, and sorting) in a single, testable entrypoint. Keeping this logic here avoids inlining CLI orchestration into helpers and centralizes side-effecting behavior for the utility.

## Args:
    None (method is instance-bound; configuration is read from the instance attributes and parsed args).

## Returns:
    None

## Raises:
    SystemExit
        Triggered when self.argparser.error(...) is called due to missing required input; this typically causes argparse to exit the process with a non-zero status.
    Any exception raised by the underlying agate.Table.from_csv(...) call
        Propagates errors from file I/O, CSV parsing, or agate internals (e.g., FileNotFoundError for a missing input file, parsing errors).
    Any exception raised by parse_column_identifiers(...)
        If the provided column identifiers are invalid or cannot be resolved, parse_column_identifiers may raise; those exceptions propagate.
    Any exception raised by table.to_csv(...)
        Errors during writing (I/O errors, permission errors, broken pipe when writing to stdout) propagate.

## State Changes:
Attributes READ:
    self.args
        - names_only (boolean) : whether to only print column names and exit
        - sniff_limit (int) : sniff limit passed to agate (with -1 treated as unlimited/None)
        - skip_lines (int) : number of leading lines to skip when reading CSV
        - columns (list[str] or similar) : user-specified columns to sort by
        - reverse (bool) : whether to reverse the sort order
    self.input_file
        - path or file-like to read CSV input from
    self.output_file
        - path or file-like to write CSV output to
    self.reader_kwargs
        - keyword args forwarded into agate.Table.from_csv
    self.writer_kwargs
        - keyword args forwarded into table.to_csv
    self.argparser
        - used to signal CLI errors (self.argparser.error(...))
    methods called that may read other internal state:
        self.get_column_types()
        self.get_column_offset()
        self.additional_input_expected()
        self.print_column_names()

Attributes WRITTEN:
    None — this method does not modify instance attributes. All operations are functional or produce external side effects (I/O). The instance state is not updated.

## Constraints:
Preconditions:
    - The instance must have parsed arguments available on self.args (the CLI parsing stage must have completed).
    - self.input_file and self.output_file must refer to valid file-like objects or paths appropriate for the intended I/O (e.g., stdout for output, stdin for input).
    - If args.names_only is True, printing column names is meaningful only if input is available; the method calls print_column_names(), which must be prepared to handle the configured input source.

Postconditions:
    - On successful completion, the output destination contains the input CSV sorted by the specified columns (or the process exits earlier if names-only or error conditions occur).
    - No instance attributes are modified by this method.
    - Any exceptions raised by agate, parsing, or I/O are propagated to the caller (or cause process exit if argparser.error is invoked).

## Behavior details (explicit steps and edge handling):
    1. names-only path:
        - If self.args.names_only is truthy, call self.print_column_names() and return immediately. No other side effects occur.
    2. input availability check:
        - If self.additional_input_expected() returns True, call self.argparser.error('You must provide an input file or piped data.').
          This signals a CLI usage error and typically terminates the process (raises SystemExit via argparse's error handling).
    3. sniff_limit handling:
        - Convert args.sniff_limit: if it equals -1, pass sniff_limit=None to agate to indicate "no limit"; otherwise pass the integer value.
    4. table construction:
        - Call agate.Table.from_csv(self.input_file, skip_lines=self.args.skip_lines, sniff_limit=sniff_limit, column_types=self.get_column_types(), **self.reader_kwargs)
        - This reads the CSV input and returns an agate.Table. Any exceptions from agate (I/O or parse errors) propagate.
    5. column identifier resolution:
        - Call parse_column_identifiers(self.args.columns, table.column_names, self.get_column_offset()) to convert CLI-specified column selectors into column index identifiers suitable for agate.Table.order_by.
        - The function uses the loaded table's column names and any offset provided by get_column_offset().
    6. sorting:
        - Call table.order_by(column_ids, reverse=self.args.reverse). This returns a new agate.Table sorted per the requested columns and direction.
    7. writing:
        - Call table.to_csv(self.output_file, **self.writer_kwargs) to write the sorted data to the output destination. Writing errors (I/O) propagate.

## Side Effects:
    - Reads input CSV data from self.input_file (may be a file path or stdin).
    - Writes sorted CSV data to self.output_file (may be a file path or stdout).
    - May print to stdout when print_column_names() is invoked.
    - May terminate the process via self.argparser.error(...) which generally raises SystemExit.
    - Uses agate library for parsing, sorting, and writing CSV data; any external resource use (file descriptors) is handled by agate/Table methods.

## `csvkit.utilities.csvsort.launch_new_instance` · *function*

## Summary:
Instantiate the CSV sort CLI utility and transfer control to its lifecycle runner, causing the csvsort command to parse arguments, read input, perform sorting, and write output.

## Description:
- Known callers and typical context:
  - Packaging entry points (console_scripts) that start the installed csvsort command at process startup.
  - Integration tests or harnesses that import the module and call this function to execute csvsort end-to-end in-process.
  - Any external runner that expects a zero-argument, importable entry point to bootstrap the csvsort behavior.
  - Typical trigger: the runtime imports the module and calls launch_new_instance() immediately when the command is invoked, or a test explicitly calls it to exercise the utility's run lifecycle.

- Why this logic is extracted into its own function rather than inlined:
  - Provides a stable, importable, and testable entry point that hides the CSVSort class instantiation details from packaging or test code.
  - Keeps bootstrapping minimal and consistent across csvkit utilities (same one-line pattern used for other utilities), simplifying packaging configuration and in-process testing.
  - Delegates all argument parsing, I/O, and processing logic to CSVSort and the CSVKitUtility runner so the wrapper remains trivial and predictable.

## Args:
- None.

## Returns:
- None.
  - The function returns implicitly after CSVSort.run() completes normally.
  - If CSVSort.run() blocks (e.g., awaiting input, though csvsort normally performs a finite processing task), the wrapper will block until run() returns or raises.
  - No success/failure value is returned; callers must infer outcome from absence/presence of exceptions or observable side effects (output files, stdout).

## Raises:
- NameError
  - Condition: The CSVSort symbol is not defined or importable in the module namespace when attempting to instantiate it (CSVSort()).
- Any exception raised by CSVSort.__init__
  - Condition: CSVSort constructor raises during instantiation (e.g., missing dependencies or constructor-time validation errors).
- Any exception raised by CSVSort.run()
  - Condition: runtime failures during argument parsing, input opening, CSV parsing/writing, column selector parsing, or explicit process termination. Examples (originating from CSVSort or the runner) include:
    - SystemExit (argparse error or explicit exit)
    - FileNotFoundError, PermissionError, OSError (I/O)
    - agate parsing errors or other agate-related exceptions
    - Column identifier parsing errors propagated from parse_column_identifiers
  - Note: This wrapper does not catch or transform exceptions; they propagate unchanged to the caller.

## Constraints:
- Preconditions:
  - The CSVSort class must be present in the module namespace and constructable.
  - Any runtime context required by CSVSort.run (for example, expected sys.argv contents, available input/output streams, or environment variables) should be prepared by the caller; this wrapper does not set up command-line arguments or I/O.
- Postconditions:
  - If the function returns normally, CSVSort.run() has completed and any side effects performed by it (reading/writing files, printing to stdout/stderr, modifying global state) have already occurred.
  - No value is returned to indicate success; callers must inspect side effects or rely on lack of exceptions.

## Side Effects:
- This function performs no direct I/O itself beyond constructing an object and calling its run method.
- All observable side effects (I/O, stdout/stderr output, file writes, sys.exit/SystemExit, global state mutation such as agate configuration) are produced by CSVSort.run() and by CSVKitUtility.run() behavior (for example, opening/closing input files).
- The wrapper does not handle resource cleanup; it relies on CSVKitUtility.run and CSVSort implementations to manage files and resources.

## Control Flow:
flowchart TD
    A[Call launch_new_instance()] --> B[Instantiate CSVSort()]
    B --> C{CSVSort.__init__ succeeds?}
    C -- no --> D[Constructor exception propagates to caller]
    C -- yes --> E[Call CSVSort.run() (delegates to CSVKitUtility.run())]
    E --> F{run() completes normally?}
    F -- yes --> G[Function returns None]
    F -- no --> H[Runtime exception or SystemExit propagates to caller]

## Examples:
- Typical packaging usage (conceptual):
  - Register csvkit.utilities.csvsort:launch_new_instance as a console_scripts entry point so the packaging runner imports the module and calls launch_new_instance() when the installed "csvsort" command is executed.

- Programmatic invocation with basic error handling:
  - Use when a test harness wants to run the utility but handle expected process-exiting behavior:
      try:
          launch_new_instance()
      except SystemExit as se:
          # Argument parsing or explicit exit occurred in CSVSort.run(); assert or log as needed
          handle_exit(se)
      except NameError:
          # CSVSort symbol not present in this runtime/module
          handle_missing_entry_point()
      except Exception as exc:
          # I/O, parsing, or other runtime errors from CSVSort.run()
          handle_runtime_error(exc)

Notes:
- For detailed behavior (registered CLI options, sniffing behavior, column selector parsing, and exact I/O semantics), consult the CSVSort component and CSVKitUtility.run documentation. This wrapper intentionally remains minimal and delegates all operational responsibilities to those components.

