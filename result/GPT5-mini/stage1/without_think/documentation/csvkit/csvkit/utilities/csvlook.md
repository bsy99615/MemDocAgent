# `csvlook.py`

## `csvkit.utilities.csvlook.CSVLook` · *class*

## Summary:
Represents the csvlook CLI command: render a CSV file (or piped CSV data) as a fixed-width, Markdown-compatible table on the console.

## Description:
This class implements the "csvlook" utility behavior. It extends CSVKitUtility and provides:
- CLI option definitions for controlling the printed table (max rows/columns/column width/precision, sniffing and inference flags).
- A main entrypoint that reads a CSV into an agate.Table and prints a fixed-width table to the configured output.

Typical usage scenarios:
- Invoked by the csvkit CLI runner that constructs a CSVLook instance, registers arguments, parses command-line options into self.args, and then calls main().
- Useful for interactive inspection of CSV files or streamed CSV data when a human-readable, column-aligned table is desirable.

Motivation and responsibility boundary:
- CSVLook isolates CLI option definitions and the flow from parsed arguments → agate.Table.from_csv → agate.Table.print_table.
- It does not itself implement CSV parsing or printing logic — that is delegated to agate.Table. CSVLook maps CLI options and runtime flags to the agate API and global agate configuration (via agate.config).

## State:
This class defines no new instance attributes beyond what CSVKitUtility provides. The following attributes are read or written by CSVLook methods; their types and invariants are described so implementers can recreate correct behavior.

- description (str, class attribute)
    - Value: 'Render a CSV file in the console as a Markdown-compatible, fixed-width table.'
    - Invariant: constant text describing the utility.

Attributes expected to exist on instances (inherited from CSVKitUtility):
- argparser (argparse.ArgumentParser-like)
    - Type: CLI argument parser supporting add_argument(...) and error(msg).
    - Usage: add_arguments() registers several options on this parser.
    - Invariant: exists before add_arguments is called.

- args (argparse.Namespace-like)
    - Type: Namespace populated after parsing command-line args.
    - Required fields read by CSVLook.main:
        - max_rows (int or None)
        - max_columns (int or None)
        - max_column_width (int or None)
        - max_precision (int or None)
        - no_number_ellipsis (bool)
        - sniff_limit (int)
        - no_inference (bool)
        - skip_lines (int or None)
        - line_numbers (bool)
    - Invariants:
        - sniff_limit is an int; CSVLook treats -1 specially (meaning "sniff entire file").
        - max_precision, if provided, is an int ≥ 0 (caller responsibility to supply sensible values).
        - These attributes must exist prior to calling main() (the CLI framework should supply them via parsing).

- input_file
    - Type: file-like object or file path accepted by agate.Table.from_csv.
    - Usage: passed to agate.Table.from_csv as the CSV source.
    - Constraint: must reference readable CSV content (file, path, or stream).

- output_file
    - Type: file-like object (text-mode) where the printed table is written.
    - Usage: passed to table.print_table.

- reader_kwargs
    - Type: dict
    - Usage: forwarded as keyword arguments to agate.Table.from_csv.
    - Invariant: mapping of CSV reader options (may be empty).

- get_column_types() (callable on self)
    - Returns: an agate.TypeTester or None as used by agate.Table.from_csv.
    - Behavior: constructed according to CLI options (see CSVKitUtility.get_column_types).

- additional_input_expected() (callable on self)
    - Returns: truthy value when the utility should expect piped STDIN instead of a file path.
    - Behavior: if truthy, main will call argparser.error to abort with a helpful message.

- agate.config (module-global configuration)
    - CSVLook may mutate agate configuration: when --no-number-ellipsis is set, CSVLook calls config.set_option('number_truncation_chars', '') which is a global change influencing how agate prints truncated numbers.

Class invariants:
- add_arguments() must be called (or the CLI framework must have already set up the parser) before parsing into self.args.
- The attributes listed above must be present and valid before calling main().
- main() does not mutate any CSVLook-specific instance state except via calling agate.config.set_option (a global side-effect).

## Lifecycle:
Creation:
- Instantiate using the CSVKitUtility constructor (CSVLook does not override __init__).
- The CLI framework should:
    1. Construct the CSVLook instance.
    2. Call add_arguments() to register options on argparser.
    3. Parse CLI args into self.args (populating the fields listed under State).
    4. Provide valid input_file, output_file, and reader_kwargs on the instance (usually set by CSVKitUtility during argument parsing/initialization).

Usage (typical sequence):
1. add_arguments() — register CLI flags:
    - --max-rows (int)
    - --max-columns (int)
    - --max-column-width (int)
    - --max-precision (int)
    - --no-number-ellipsis (flag)
    - -y/--snifflimit (int, default 1024)
    - -I/--no-inference (flag)
2. After argument parsing, call main():
    - main() first calls additional_input_expected() and, if it returns truthy, calls self.argparser.error('You must provide an input file or piped data.') to abort.
    - Builds a kwargs dict for print_table; sets 'max_precision' only when args.max_precision is not None.
    - If args.no_number_ellipsis is truthy, calls agate.config.set_option('number_truncation_chars', '') to disable number truncation ellipsis globally.
    - Computes sniff_limit: uses args.sniff_limit unless it equals -1, in which case sniff_limit is set to None (allowing agate to sniff the whole input).
    - Calls agate.Table.from_csv with:
        - self.input_file
        - skip_lines=self.args.skip_lines
        - sniff_limit=sniff_limit
        - column_types=self.get_column_types()
        - line_numbers=self.args.line_numbers
        - plus any self.reader_kwargs
    - Calls table.print_table with:
        - output=self.output_file
        - max_rows=self.args.max_rows
        - max_columns=self.args.max_columns
        - max_column_width=self.args.max_column_width
        - plus any print kwargs from earlier (e.g., max_precision)
3. Destruction / cleanup:
    - CSVLook does not define __enter__/__exit__ or close methods. The caller (CLI runner) is responsible for opening/closing input_file and output_file if they are file handles.
    - The only cross-cutting cleanup to be aware of: calling main() with --no-number-ellipsis modifies agate.config globally. If a caller needs previous config restored, it must do so; CSVLook does not revert config changes.

## Method Map:
flowchart TD
    A[add_arguments()] --> B[Argument parsing (external)]
    B --> C[main()]
    C --> D[additional_input_expected()]
    D -- True --> E[argparser.error('You must provide an input file or piped data.')]
    D -- False --> F[maybe set agate.config option]
    F --> G[agate.Table.from_csv(..., column_types=self.get_column_types(), sniff_limit=...)]
    G --> H[table.print_table(output=self.output_file, ...)]
    C --> I[get_column_types()] 
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style C fill:#bbf,stroke:#333,stroke-width:1px
    style G fill:#bfb,stroke:#333,stroke-width:1px
    style H fill:#ffb,stroke:#333,stroke-width:1px

Notes:
- get_column_types() is a dependency provided by CSVKitUtility; it influences the column_types argument passed to agate.Table.from_csv.
- additional_input_expected() is used to detect missing input.

## Raises:
- add_arguments(): does not raise under normal operation (delegates to argparser.add_argument).
- main():
    - If additional_input_expected() is truthy, main calls self.argparser.error('You must provide an input file or piped data.'). Typical behavior of argparser.error is to print an error and exit by raising SystemExit; the exact behavior depends on the argparser implementation provided by CSVKitUtility.
    - Runtime exceptions propagated from agate.Table.from_csv or agate.Table.print_table (file I/O errors, parsing errors, invalid format/locale strings, etc.) are not caught by CSVLook and will propagate to the caller.
    - If expected attributes on self are missing (e.g., self.input_file, self.args, self.reader_kwargs, or the fields under self.args referenced in main), AttributeError will be raised. It is the caller/framework responsibility to ensure these are present before calling main().

## Example:
- Typical high-level sequence (pseudo-code for a CLI runner):
    1. inst = CSVLook()                       # CSVKitUtility constructor sets up argparser
    2. inst.add_arguments()                   # register csvlook-specific options
    3. parse CLI args into inst.args          # e.g., using inst.argparser.parse_args()
    4. ensure inst.input_file and inst.output_file are set by the runner
    5. inst.main()                            # performs sniffing, builds agate.Table, prints table

A concrete minimal scenario (conceptual, not runnable code here):
    - User runs: csvlook data.csv
    - CLI runner sets inst.args.input_path='data.csv', sets inst.input_file to path or file handle, populates other flags with defaults, then calls inst.main() and receives the printed table on stdout.

### `csvkit.utilities.csvlook.CSVLook.add_arguments` · *method*

## Summary:
Adds command-line options to the utility's argument parser that control how table output is formatted and how input CSVs are parsed; mutates the parser by registering several flags and options.

## Description:
This method registers the following CLI options on self.argparser:
- Controls display truncation and numeric formatting (--max-rows, --max-columns, --max-column-width, --max-precision, --no-number-ellipsis).
- Controls CSV dialect sniffing behavior (-y / --snifflimit).
- Controls whether type inference is performed (-I / --no-inference).

Known callers and context:
- Called during CLI setup/initialization when the utility constructs or extends an argparse.ArgumentParser for this command so the command accepts these options before parsing user input.
- Typical lifecycle stage: invoked while preparing the command's argument parser (before parsing argv and before the command's main execution logic that reads and formats CSV data).
- Why it is its own method: groups and centralizes all CLI option registration for the csvlook utility. Separating argument registration into its own method keeps parser construction modular and reusable, and avoids inlining many add_argument calls in the initialization or run logic.

## Args:
This method takes no external arguments; it operates on the object's attribute:
- self.argparser: must be an argument parser-like object exposing add_argument(name_or_flags..., **kwargs).

The options registered:
- --max-rows
    - dest: max_rows
    - type: int
    - default: None (no default set by this method)
    - description: The maximum number of rows to display before truncating the data.
- --max-columns
    - dest: max_columns
    - type: int
    - default: None
    - description: The maximum number of columns to display before truncating the data.
- --max-column-width
    - dest: max_column_width
    - type: int
    - default: None
    - description: Truncate all columns to at most this width; truncated contents are replaced with an ellipsis.
- --max-precision
    - dest: max_precision
    - type: int
    - default: None
    - description: The maximum number of decimal places to display; excess precision will be represented with an ellipsis.
- --no-number-ellipsis
    - dest: no_number_ellipsis
    - action: store_true
    - type: boolean flag; when present sets dest to True, otherwise False
    - default: False
    - description: Disable the numeric ellipsis behavior when --max-precision is exceeded.
- -y, --snifflimit
    - dest: sniff_limit
    - type: int
    - default: 1024
    - description: Limit CSV dialect sniffing to this many bytes. Special values:
        * 0 — disable sniffing entirely
        * -1 — sniff the entire file
- -I, --no-inference
    - dest: no_inference
    - action: store_true
    - type: boolean flag; when present sets dest to True, otherwise False
    - default: False
    - description: Disable type inference when parsing input; prevents automatic reformatting of values.

## Returns:
- None. The method's observable effect is the registration of arguments on self.argparser.

## Raises:
- AttributeError: If self.argparser does not exist or is None (because the method accesses self.argparser.add_argument).
- Any exceptions raised by the underlying parser.add_argument implementation (for example, if duplicate option strings or invalid argument specification are provided) will propagate unchanged.

## State Changes:
Attributes READ:
- self.argparser (accessed to call add_argument)

Attributes WRITTEN / mutated:
- self.argparser (its internal state is mutated: new arguments/options are registered; no assignment to self.argparser is performed)

## Constraints:
Preconditions:
- self.argparser must be set to an object that implements add_argument(name_or_flags..., **kwargs) with semantics compatible with argparse.ArgumentParser.add_argument.
- The option strings registered must not conflict with previously-registered options on the same parser (otherwise parser.add_argument will raise).

Postconditions:
- After the call, the argument parser referenced by self.argparser will accept the listed options and populate parsed Namespace attributes with the dest names: max_rows, max_columns, max_column_width, max_precision, no_number_ellipsis, sniff_limit, no_inference.
- Default values provided by this method: sniff_limit == 1024; boolean flags default to False unless the parser elsewhere overrides defaults.

## Side Effects:
- Mutates the internal registration state of self.argparser (command-line option definitions are added).
- No I/O is performed.
- No network or external service calls are made.
- No other object state outside self.argparser is modified by this method.

### `csvkit.utilities.csvlook.CSVLook.main` · *method*

## Summary:
Orchestrates reading the input CSV (from a file or piped stdin), constructs an agate Table with configured inference options, and renders it as a fixed-width table to the configured output. This is the CLI entrypoint that performs no return value but triggers I/O and may alter agate configuration.

## Description:
This method is the primary runtime entrypoint invoked when the CSVLook utility is executed from the command line (i.e., after argument parsing and CLI dispatch). It performs validation that required input is present, prepares formatting and inference options, constructs an agate.Table from the CSV input, and calls the table's print routine to produce human-readable console/tabular output.

Known callers and context:
- Called by the CLI dispatch/run logic that executes CSVKit utility classes (the typical lifecycle: create utility instance → parse args → call main/run to perform the operation).
- Lifecycle stage: invoked after CLI arguments have been parsed and before program termination; it is responsible for the core read-and-render pipeline of the csvlook tool.

Why this is a separate method:
- Encapsulates the full command behavior for a single utility (input validation → table construction → rendering), keeping argument parsing and other plumbing separate and making it easier to test and override behavior in subclasses.

## Args:
None (method operates on instance state: self.args, self.input_file, self.output_file, etc.)

## Returns:
None
- The method does not return a value; its effect is to perform I/O (read input, write output) and to possibly modify global agate configuration (see Side Effects).

## Raises:
- Invokes self.argparser.error('...') when additional_input_expected() is truthy. The actual effect depends on the parser implementation; typical parsers will emit an error message and terminate the process (e.g., by raising SystemExit).
- Any exception raised by agate.Table.from_csv may propagate (for example, I/O errors when opening/reading the input file, agate parsing exceptions, or errors raised by invalid column_types).
- Any exception raised by table.print_table may propagate (for example, errors writing to output_file or errors in formatting).
- Any exception raised by config.set_option will propagate (if agate.config rejects the option or value).

## State Changes:
Attributes READ:
- self.args.max_precision
- self.args.no_number_ellipsis
- self.args.sniff_limit
- self.args.skip_lines
- self.args.line_numbers
- self.args.max_rows
- self.args.max_columns
- self.args.max_column_width
- self.input_file
- self.output_file
- self.reader_kwargs
- self.argparser (only to call error)
- self.get_column_types() (method called; reads from self.args per its implementation)
- self.additional_input_expected() (method called)

Attributes WRITTEN:
- None on the CSVLook instance itself. The method does not assign to any self.<attr>.

## Constraints:
Preconditions:
- self.args must exist and expose the attributes accessed above (max_precision, no_number_ellipsis, sniff_limit, skip_lines, line_numbers, max_rows, max_columns, max_column_width).
- self.input_file must be a path string or a file-like object acceptable to agate.Table.from_csv.
- self.output_file must be a writable file-like object or path accepted by agate.Table.print_table.
- self.reader_kwargs must be a dict of keyword arguments acceptable to agate.Table.from_csv.
- self.get_column_types() must return a value acceptable to agate.Table.from_csv (typically an agate.TypeTester or None).
- self.additional_input_expected() must be callable and return a truthy/falsy indicator consistent with whether the utility should require an explicit input file or piped data.

Postconditions:
- If additional_input_expected() returned truthy, the parser's error handler is invoked and normal execution does not proceed past that point (depending on the parser behavior).
- If execution proceeds, an agate.Table instance is created from the specified input and the table's print_table method is invoked to produce output according to the supplied CLI options.
- No instance attributes are mutated by this method.

## Side Effects:
- Calls config.set_option('number_truncation_chars', '') when self.args.no_number_ellipsis is truthy, which mutates agate's global configuration.
- Reads the input CSV (I/O): agate.Table.from_csv will open/read self.input_file (or consume piped stdin) and may perform type inference and parsing.
- Writes output (I/O): table.print_table writes rendered table output to self.output_file (console or a file).
- May cause program termination via the argument parser's error handler (self.argparser.error), depending on its implementation.

## Behavior details and edge cases:
- Precision handling: if self.args.max_precision is not None, a keyword 'max_precision' with that integer value is forwarded to table.print_table. If max_precision is None, no 'max_precision' is passed and default printing precision is used.
- Number ellipsis: if self.args.no_number_ellipsis is truthy, the method disables number ellipsis globally by calling agate.config.set_option('number_truncation_chars', ''). This changes agate's rendering behavior for numbers for the duration of the process (global effect).
- Sniff limit: the CLI argument sniff_limit is interpreted such that a value of -1 becomes None before being passed to agate.Table.from_csv; other integers are passed through directly. (agate.Table.from_csv treats None as "no limit"/default behavior.)
- Column type inference: column_types passed to agate.Table.from_csv come from self.get_column_types(), which typically returns an agate.TypeTester configured from CLI options (e.g., honoring --no-inference). If inference is disabled via those options, get_column_types will cause from_csv to skip or limit inference as appropriate.

## `csvkit.utilities.csvlook.launch_new_instance` · *function*

## Summary:
Instantiate the csvlook command handler and execute its runtime lifecycle (construct CSVLook and run it), causing the full CLI execution flow (argument handling, input opening, main processing, cleanup) to occur.

## Description:
- Known callers within the codebase and typical contexts:
    - No direct internal callers were located in the repository search. This function is intended to be used as the process entry point (console_scripts / package entry point) for the csvlook command-line utility. Packaging tools (setuptools/poetry) typically reference csvkit.utilities.csvlook:launch_new_instance so that running the installed "csvlook" command invokes this function.
    - It may also be called by a top-level CLI runner or test harness that wishes to run the csvlook utility in-process (for example, integration tests that import the entry point and call it directly).

- Why this logic is extracted into a standalone function:
    - Serves as a stable importable entry point that packaging systems can point to (no arguments, trivial signature).
    - Keeps process-level initialization (instantiation + run) out of module import-time code and in a small, testable wrapper.
    - Separates the responsibility of "starting" the utility from the implementation details of CSVLook and the CLI framework (CSVKitUtility).

## Args:
    None

## Returns:
    None (implicitly returns None on normal completion).
    - The function does not return a value; its purpose is to perform side effects (run the CLI command).
    - Possible observable terminal outcomes:
        - Normal return (None) when CSVKitUtility.run completes without raising.
        - SystemExit may be raised by the underlying argument parser (e.g., on parse error or calls to argparser.error).
        - Other exceptions raised by CSVLook/CSVKitUtility (I/O errors, agate parsing/printing errors, AttributeError) propagate out.

## Raises:
    - SystemExit: May be raised by the underlying argument parser if argument parsing fails or argparser.error is invoked by CSVLook or framework code.
    - Any exception raised by CSVLook.__init__ or CSVKitUtility.run: including but not limited to FileNotFoundError, OSError, agate-related exceptions, or AttributeError if required attributes are missing on the instance.
    - No exceptions are explicitly raised in this wrapper; it simply propagates exceptions from the instantiated object's lifecycle.

## Constraints:
- Preconditions:
    - The CSVLook class must be importable and behave as a CSVKitUtility subclass (implementing main() and cooperating with CSVKitUtility.run expectations).
    - Environment expected by CSVLook and CSVKitUtility.run (e.g., sys.argv for argument parsing, or test harness that has set args on the instance) must be established prior to invocation if required by the CLI framework.
    - Packaging/runtime should ensure that any resources (stdin, stdout) required by CSVLook are available and appropriately connected.

- Postconditions:
    - On successful completion (no exception), CSVKitUtility.run semantics apply:
        - If run opened an input file (not suppressed by override flags), that file will have been closed before launch_new_instance returns.
        - Any global configuration changes applied by CSVLook.main (for example, agate.config modifications such as disabling number truncation ellipsis) will remain in effect after return unless explicitly restored.
    - If an exception is raised, the caller should assume partial side effects may have occurred (e.g., partially written output, mutated global config, partially opened/closed files).

## Side Effects:
- Instantiates CSVLook(), which may register CLI options or set up parser state during its construction (depending on CSVLook implementation and CSVKitUtility).
- Calls CSVLook.run(), which performs:
    - File/stream I/O: opening input files, reading CSV content, writing to output_file.
    - Interaction with agate APIs: Table.from_csv and Table.print_table may execute; agate.config may be mutated (e.g., number_truncation_chars changed when --no-number-ellipsis is used).
    - Warning suppression context while main() runs (CSVKitUtility.run temporarily suppresses certain agate warnings when configured).
    - Possible process exit via SystemExit triggered by argument parsing errors.
- No return value; effects are visible externally via I/O and global state changes.

## Control Flow:
flowchart TD
    Start --> Instantiate[Instantiate CSVLook()]
    Instantiate --> CallRun[Call CSVLook.run()]
    CallRun --> RunSuccess[run() returns normally]
    CallRun --> RunError[run() raises Exception/SystemExit]
    RunSuccess --> End[Function returns None]
    RunError --> EndError[Exception propagates to caller]
    style Instantiate fill:#bbf,stroke:#333,stroke-width:1px
    style CallRun fill:#bfb,stroke:#333,stroke-width:1px
    style RunError fill:#f99,stroke:#333,stroke-width:1px

## Examples:
- Typical packaging usage (conceptual, non-code description):
    - In your project's packaging configuration, declare a console script entry point that references csvkit.utilities.csvlook:launch_new_instance. When the user runs the installed "csvlook" command, the packaging runtime imports csvkit.utilities.csvlook and calls launch_new_instance(), which constructs CSVLook and runs the full CLI flow (argument parsing, input open, table generation, output).

- Running in-process from a test or harness (conceptual):
    - A test may import launch_new_instance and call it directly to exercise csvlook end-to-end. The test harness should prepare the environment (set sys.argv or configure CSVLook/CSVKitUtility state) and capture stdout/stderr. Be prepared to catch SystemExit or other propagated exceptions to assert error behavior.
    - Error handling advice: call launch_new_instance() inside a try/except block that explicitly catches SystemExit and other expected exceptions (e.g., OSError) if the test/harness intends to assert on failure modes rather than allowing the process to terminate.

