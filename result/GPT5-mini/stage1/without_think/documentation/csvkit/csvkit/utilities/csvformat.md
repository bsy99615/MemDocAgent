# `csvformat.py`

## `csvkit.utilities.csvformat.CSVFormat` · *class*

block without including Python source. Then I will run VERIFY to self-evaluate the output.

Action: WRITE
<DOCUMENTATION>
## Summary:
CSVFormat is a CLI utility class that converts CSV input into a CSV-like output with customizable formatting (delimiter, quoting, escape, line terminator, and optional header handling). It adapts writer options from parsed CLI arguments and streams input rows through an agate CSV reader to an agate CSV writer.

## Description:
CSVFormat is intended for use as a command-line utility (a subclass of CSVKitUtility) to take CSV data from files or stdin and write it to an output stream (typically stdout) using explicitly configured CSV writer options. Typical scenarios:
- Reformatting CSV files to use a different delimiter, quote character, or quoting mode.
- Converting a CSV lacking headers into one with generated default headers.
- Emitting output rows without a header row.

Callers / factories:
- Created and invoked by the csvkit CLI framework (CSVKitUtility-derived entrypoints). In a programmatic context, instantiate the class, configure or parse command-line arguments into self.args, then call main().

Motivation and responsibility boundary:
- Responsibility: centralize logic for mapping CLI arguments to agate CSV writer options and for streaming rows from an agate reader to an agate writer while handling header-related transformations.
- Boundary: CSVFormat does not implement argument parsing mechanics itself (it adds recognized args via add_arguments()); it delegates low-level CSV IO to agate.csv.reader and agate.csv.writer and relies on CSVKitUtility facilities for I/O streams, argument parsing, and helper methods like skip_lines() and additional_input_expected().

## State:
Class-level attributes:
- description (str): Human-readable description used by the CLI framework: 'Convert a CSV file to a custom output format.'
- override_flags (list[str]): Flags that the CLI framework may override for parsing/behavior: ['L', 'blanks', 'date-format', 'datetime-format'].

Instance-visible attributes used by this class (inherited or set up by CSVKitUtility and populatable via parsed CLI args):
- argparser (argparse.ArgumentParser): CLI parser instance (inherited).
- args (argparse.Namespace): Parsed CLI arguments. Relevant keys accessed by CSVFormat:
  - args.skip_header (bool): If True, skip the input header row in the output. Default: False.
  - args.out_delimiter (str or None): User-specified output delimiter character. Default: None.
  - args.out_tabs (bool): If True, output delimiter is a tab (overrides out_delimiter). Default: False.
  - args.out_quotechar (str or None): Output quote character to pass to writer. Default: None.
  - args.out_quoting (int or None): Quoting style to pass to writer. Allowed values: 0, 1, 2, 3. Default: None.
  - args.out_doublequote (bool or None): Whether double quotes should be doubled in output. Note: the argument defined uses action='store_false' to set False when option provided; otherwise inherits CSVKitUtility default. Default: (inherited).
  - args.out_escapechar (str or None): Escape character for the output writer. Default: None.
  - args.out_lineterminator (str or None): Line terminator to pass to writer. Default: None.
  - args.no_header_row (bool): If True, treat first input row as data (not header) and replace header with generated defaults. Default: False.
  - args.line_numbers (bool): If True, include line numbers in writer output via kwargs. Default: False.

Other runtime state (provided by CSVKitUtility and used here):
- reader_kwargs (dict): Reader options passed to agate.csv.reader (set up by parent utility).
- writer_kwargs (dict): Writer options passed to agate.csv.writer (populated by CSVFormat via _extract_csv_writer_kwargs).
- output_file (file-like object): Destination file-like object for the writer (typically stdout).
- Methods inherited/used: skip_lines(), additional_input_expected(). These affect input iteration and CLI prompting behavior.

Class invariants:
- writer_kwargs returned by _extract_csv_writer_kwargs will only include keys recognized by agate.csv.writer: possible keys include line_numbers, delimiter, quotechar, quoting, doublequote, escapechar, lineterminator.
- If args.out_tabs is True then 'delimiter' in writer_kwargs is '\t' and any args.out_delimiter is ignored.
- out_quoting, if provided, must be one of {0,1,2,3} (enforced by argparse choices).

## Lifecycle:
Creation:
- Instantiate with CSVFormat() (no explicit __init__ in this class). The typical flow in the CLI framework:
  1. CSVKitUtility subclass is constructed; CLI parsing is performed which populates self.args.
  2. add_arguments() is called by the framework to register CSVFormat-specific options before parsing.

Usage:
- Typical sequence:
  1. add_arguments() is called (by the CLI framework) to register options the user can pass on the command line.
  2. After argument parsing, optionally call _extract_csv_writer_kwargs() to obtain writer configuration derived from self.args. The method returns a dict of kwargs to pass to agate.csv.writer.
  3. main() is called to perform the conversion:
     - If additional_input_expected() is True and no input provided, a message is written to stderr informing the user it is waiting on stdin.
     - An agate CSV reader is created over the input (skip_lines() provides the iterator).
     - An agate CSV writer is created using writer_kwargs and output_file.
     - If args.no_header_row is True, the first input row is consumed as data and default headers are generated and prepended so that output has header row followed by the original first row.
     - If args.skip_header is True, the first row of the reader is dropped (no header in output).
     - The writer streams all remaining rows via writer.writerows(reader).

Sequencing constraints:
- _extract_csv_writer_kwargs should be called only after self.args has been parsed and is available.
- main() expects reader_kwargs and writer_kwargs to be set up; writer_kwargs is typically obtained from calling _extract_csv_writer_kwargs() (the CLI framework may populate this before main()).
- No explicit cleanup (close) is performed here; the writer writes to self.output_file which the framework manages.

Destruction:
- No special cleanup required by CSVFormat itself. Output file management is the responsibility of the surrounding CLI framework (CSVKitUtility). If using custom file objects, callers should close them externally.

## Method Map:
Graph of interactions and typical call flow:
add_arguments --> (registers CLI flags used by args)
_extract_csv_writer_kwargs --> returns writer_kwargs (line_numbers, delimiter, quotechar, quoting, doublequote, escapechar, lineterminator)
main:
  - additional_input_expected() (from parent) [checks whether to prompt]
  - skip_lines() (from parent) --> provides input iterator to:
    agate.csv.reader(reader_iterator, **reader_kwargs) --> reader
  - agate.csv.writer(output_file, **writer_kwargs) --> writer
  - conditional transformations:
      if args.no_header_row: consume first row -> headers = make_default_headers(len(_row)) -> prepend headers
      if args.skip_header: consume one row (skip)
  - writer.writerows(reader) (streams remaining rows to output)

(Visualization hint: add_arguments and _extract_csv_writer_kwargs are configuration; main orchestrates reader -> optional header handling -> writer.)

## Raises:
Explicit/observable exceptions and trigger conditions:
- StopIteration: If the input iterator has no rows and code attempts to consume a row with next(reader) when args.no_header_row or args.skip_header is True, a StopIteration will be propagated.
- Exceptions raised by the underlying agate CSV library: agate.csv.reader(...) or agate.csv.writer(...)/writer.writerows(...) may raise parsing/IO-related exceptions (for example on malformed CSV input or write failures). Those exceptions are not raised directly by CSVFormat but will propagate unless caught by callers.
- AttributeError: If self.args or required attributes provided by CSVKitUtility (e.g., reader_kwargs, output_file) are missing or misconfigured, attribute access in CSVFormat will raise AttributeError. Proper use requires the surrounding CLI framework to establish those attributes.

## Example:
A typical (conceptual) usage flow without showing source code lines:
1. Framework constructs CSVFormat and calls add_arguments() to register options.
2. User runs the CLI and argument parsing populates self.args (for example: out-tabs = True, skip-header = False).
3. The framework (or user code) calls _extract_csv_writer_kwargs() to build writer options from self.args; this returns a dict such as {'delimiter': '\t', 'quotechar': '"', 'quoting': 0}.
4. main() is invoked:
   - If no input file and additional_input_expected() is True, a message is printed to stderr indicating stdin is awaited.
   - The input iterator is wrapped by agate.csv.reader(...).
   - An agate CSV writer is created with the writer kwargs and output_file.
   - Header handling occurs based on args.no_header_row and args.skip_header.
   - writer.writerows(reader) streams the rows to output.
5. After main() returns, the CLI framework finalizes/flushes the output stream as needed.

Notes:
- Do not call _extract_csv_writer_kwargs() before args are parsed; it depends on values stored in self.args.
- The class delegates CSV read/write semantics to agate; consult agate for low-level CSV dialect behavior.

### `csvkit.utilities.csvformat.CSVFormat.add_arguments` · *method*

## Summary:
Register a set of output-formatting command-line options on the instance argument parser, mutating self.argparser so the utility can control CSV output appearance (delimiter, quoting, header emission, line terminator, etc.).

## Description:
This method centralizes registration of CLI options that affect how CSV output is formatted. It is designed to be invoked during CLI construction — specifically, after self.argparser (an argparse.ArgumentParser-like object) has been created and before parsing user input. No explicit callers are present in the provided snippet; the method is intended for use by CSVKitUtility subclasses or the CSVFormat command's initialization routine to keep option registration consistent across utilities.

Why separate this into its own method:
- Groups all output-related flags in one place for readability and maintainability.
- Enables reuse across multiple commands that need identical output options without duplicating add_argument calls.
- Simplifies testing of CLI option registration.

## Args (method parameters):
This method takes no arguments.

## Arguments added to self.argparser (per-option details):
- -E, --skip-header
    - dest: skip_header
    - type: boolean flag (action='store_true')
    - default: argparse default for store_true (False when absent)
    - effect: When supplied on the command line, sets skip_header to True; instructs the program not to write a header row.
- -D, --out-delimiter
    - dest: out_delimiter
    - type: str
    - default: None (not set here)
    - effect: Sets the character used to delimit fields in output CSV.
- -T, --out-tabs
    - dest: out_tabs
    - type: boolean flag (action='store_true')
    - default: False
    - effect: When present, marks output as tab-delimited. Help text documents that this overrides -D if both are supplied.
- -Q, --out-quotechar
    - dest: out_quotechar
    - type: str
    - default: None
    - effect: Sets the character used to quote fields in output CSV.
- -U, --out-quoting
    - dest: out_quoting
    - type: int
    - allowed values: 0, 1, 2, 3
    - default: None
    - effect: Selects the quoting style (mapped as: 0 = Quote Minimal, 1 = Quote All, 2 = Quote Non-numeric, 3 = Quote None).
- -B, --out-no-doublequote
    - dest: out_doublequote
    - type: boolean flag (action='store_false')
    - default: argparse default for store_false (True when absent)
    - effect: When supplied, sets out_doublequote to False, disabling doubling of quote characters inside quoted fields.
- -P, --out-escapechar
    - dest: out_escapechar
    - type: str
    - default: None
    - effect: Character used to escape the delimiter when quoting is disabled (quoting style 3) or to escape the quote character when double-quote doubling is disabled.
- -M, --out-lineterminator
    - dest: out_lineterminator
    - type: str
    - default: None
    - effect: Sets the string used to terminate lines in the output CSV.

## Returns:
None. The method returns nothing; it exists for the side effect of registering arguments on self.argparser.

## Raises:
- No exceptions are explicitly raised by this method in the source. However:
    - If self.argparser is missing or None, attempting to access self.argparser.add_argument will raise AttributeError.
    - Any exception raised by the underlying parser implementation's add_argument (for example, if the parser rejects an option definition) will propagate unchanged.

## State Changes:
- Attributes READ:
    - self.argparser (accessed to call add_argument repeatedly)
- Attributes WRITTEN:
    - self.argparser (mutated by adding new argument definitions; the parser's internal action/option registry is modified)

## Constraints:
- Preconditions:
    - self.argparser must be a parser object that implements add_argument(name_or_flags, ...) with semantics compatible with argparse.ArgumentParser.
    - Call this method before parsing the command-line arguments; adding arguments after parsing does not affect an already-parsed namespace.
- Postconditions:
    - After calling this method, parsing the command line with self.argparser will produce a namespace containing attributes: skip_header, out_delimiter, out_tabs, out_quotechar, out_quoting, out_doublequote, out_escapechar, and out_lineterminator (each present if supplied, otherwise at their argparse defaults).
    - The parser will accept the listed flags and option forms.

## Side Effects:
- Mutates the provided argument parser by registering multiple options.
- No file, network, or external I/O is performed by this method.
- No other instance attributes are modified directly by this method (only the parser object is changed).

### `csvkit.utilities.csvformat.CSVFormat._extract_csv_writer_kwargs` · *method*

## Summary:
Build and return a dictionary of CSV writer keyword arguments by reading CLI-parsed options from self.args; does not modify self.

## Description:
This helper inspects the parsed command-line options available on self.args and produces a dict suitable for passing as keyword arguments to the CSV writer (e.g., agate.csv.writer(output_file, **kwargs)). It centralizes mapping and precedence rules so that the writer configuration is computed in one place.

Known callers and context:
- Within this file, CSVFormat.main constructs a writer using self.writer_kwargs: writer = agate.csv.writer(self.output_file, **self.writer_kwargs). This method returns the same shape of dictionary that should be assigned to self.writer_kwargs before main constructs the writer.
- The method is intended to be called during option-processing or initialization when the utility prepares writer configuration; the source does not force when it must be called — it only returns the dict.

Why this is a separate method:
- Encapsulates CLI-to-writer mapping and precedence rules (so other code does not duplicate them).
- Makes the mapping consultable and unit-testable independent of file I/O or writer creation.

## Args:
This method accepts no parameters.

It reads these attributes from self.args (exact attribute names expected):
- line_numbers (bool or truthy): if truthy, include 'line_numbers': True
- out_tabs (bool or truthy): if truthy, set delimiter to '\t' (this takes precedence over out_delimiter)
- out_delimiter (str or None): used as 'delimiter' when out_tabs is falsy and out_delimiter is truthy
- out_quotechar (str or None): maps to 'quotechar'
- out_quoting (int or None): maps to 'quoting'; CLI defines allowed choices 0,1,2,3
- out_doublequote (bool or None): maps to 'doublequote'
- out_escapechar (str or None): maps to 'escapechar'
- out_lineterminator (str or None): maps to 'lineterminator'

Notes on attribute access:
- The method reads these attributes via direct attribute access (self.args.line_numbers, self.args.out_tabs, self.args.out_delimiter) and via getattr(self.args, 'out_<arg>') for the quote/quoting/doublequote/escapechar/lineterminator group. If any expected attribute is missing from self.args, an AttributeError will be raised.

## Returns:
dict[str, Any]: A dictionary containing zero or more of these keys:
- 'line_numbers': True (only present when self.args.line_numbers is truthy)
- 'delimiter': str (either '\t' if out_tabs is truthy, otherwise the truthy value of self.args.out_delimiter)
- 'quotechar': str (from self.args.out_quotechar)
- 'quoting': int (from self.args.out_quoting; expected 0..3 per CLI)
- 'doublequote': bool (from self.args.out_doublequote)
- 'escapechar': str (from self.args.out_escapechar)
- 'lineterminator': str (from self.args.out_lineterminator)

Edge-case/behavior details:
- The method omits any option whose corresponding self.args value is None or otherwise falsy where the code checks truthiness (specifically for out_delimiter and out_tabs). For the five options iterated with getattr, it only includes them when their value is not None (the code uses "is not None" check).
- If out_delimiter is an empty string (''), it is treated as falsy and will not be included; multi-character delimiters are accepted as-is.
- If no options relevant to the writer are set, the method returns an empty dict.

## Raises:
- AttributeError: If self.args does not exist or lacks any of the accessed attributes (e.g., self.args.line_numbers, self.args.out_tabs, or any out_<arg> attribute accessed via getattr). The method does not catch or transform these errors.

## State Changes:
Attributes READ:
- self.args and the listed attributes: line_numbers, out_tabs, out_delimiter, out_quotechar, out_quoting, out_doublequote, out_escapechar, out_lineterminator

Attributes WRITTEN:
- None. The method returns a new dict and does not mutate self or other external objects.

## Constraints:
Preconditions:
- self.args must be present and be an object (typically argparse.Namespace) exposing the attributes documented above.
- If present, out_quoting should conform to the CLI's allowed values (0, 1, 2, 3) — the method accepts any integer but the CLI enforces choices.

Postconditions:
- Returned dict contains only keys for options that were explicitly set (or truthy where checked) and never contains keys for unset/None options.
- 'delimiter' key follows precedence: if out_tabs is truthy then delimiter == '\t'; else if out_delimiter is truthy then delimiter == out_delimiter; otherwise no 'delimiter' key is present.
- The returned dict keys are a subset of {'line_numbers','delimiter','quotechar','quoting','doublequote','escapechar','lineterminator'}.

## Side Effects:
- None. The method performs no I/O, network activity, or mutation of objects outside of constructing and returning the kwargs dict.

## Reimplementation algorithm (step-by-step):
1. Create an empty dict.
2. If self.args.line_numbers is truthy, set dict['line_numbers'] = True.
3. If self.args.out_tabs is truthy, set dict['delimiter'] = '\t'.
   Else if self.args.out_delimiter is truthy, set dict['delimiter'] = self.args.out_delimiter.
4. For each of the names ('quotechar','quoting','doublequote','escapechar','lineterminator'):
   a. Read value = getattr(self.args, f'out_{name}').
   b. If value is not None, set dict[name] = value.
5. Return the dict.

### `csvkit.utilities.csvformat.CSVFormat.main` · *method*

## Summary:
Initialize CSV reader and writer for this utility, apply header-handling flags (synthesizing or skipping a header row as requested), and stream all input rows to the configured output.

## Description:
This method is the runtime entry point for the CSVFormat utility's processing stage. It is invoked when the csvformat CLI utility is executed — typically as part of the CSVKit CLI dispatch where CSVKitUtility (the base class) calls the subclass main() to perform its work. main() separates concerns: it prepares input and output I/O objects (reader and writer), enforces CLI header-related flags, and then streams rows from the reader into the writer. Keeping this logic in a dedicated method keeps CLI wiring (argument parsing, setup) separate from the row-processing pipeline and makes the header-handling behavior explicit and testable.

Known callers and invocation context:
    - The CSVKit CLI runtime (via CSVKitUtility.run or equivalent dispatch) calls this method when the csvformat utility is executed from the command line.
    - This method runs in the final phase of the utility lifecycle (after argument parsing and any pre-run configuration), and performs the actual file/stream transformation work.

Why this logic is its own method:
    - It is the core execution step of the utility and must be invoked by the CLI dispatch mechanism.
    - It groups reader/writer initialization and header-handling logic that applies to the whole run, avoiding duplication across other helpers and making the pipeline easy to test and reason about.

## Args:
    None (the method uses instance state).

## Returns:
    None.
    - Normal completion: returns implicitly None after all rows have been written to the configured output.
    - There is no meaningful return value; the work is performed via side effects (writing to output_file and possibly stderr).

## Raises:
    StopIteration
        - When called with self.args.no_header_row and the input iterator (reader) is empty, next(reader) will raise StopIteration.
        - When called with self.args.skip_header and the input iterator is empty, next(reader) will raise StopIteration.
    Any exceptions raised by agate.csv.reader or agate.csv.writer
        - If CSV parsing fails, or invalid reader/writer keyword arguments are supplied (from self.reader_kwargs or self.writer_kwargs), the underlying agate CSV functions may raise parsing or configuration errors; these propagate.
    OSError / IOError (or subclasses)
        - Underlying file I/O errors (when writing to self.output_file) can be raised by the writer or the file object.
    Any exceptions raised by make_default_headers or agate utilities
        - Rare: if agate or make_default_headers throws an exception (e.g., agate not available), it will propagate.

## State Changes:
    Attributes READ:
        - self.reader_kwargs (dict): used when calling agate.csv.reader(...)
        - self.writer_kwargs (dict): used when calling agate.csv.writer(...)
        - self.args (argparse.Namespace-like): read for flags:
            * self.args.no_header_row (bool)
            * self.args.skip_header (bool)
        - self.output_file (file-like object): passed to agate.csv.writer(...) and eventually written to
        - self.additional_input_expected() (method): queried to determine whether to print a waiting message to stderr
        - self.skip_lines() (method): called to obtain the input iterable to pass to agate.csv.reader(...)
    Attributes WRITTEN:
        - None. This method does not assign to any self.<attr> fields.

## Constraints:
    Preconditions (what must be true before calling):
        - self.reader_kwargs and self.writer_kwargs should be dictionaries (or mapping) appropriate for agate.csv.reader and agate.csv.writer respectively.
        - self.output_file must be a writable, file-like object compatible with agate.csv.writer (it must support a write() method and accept the produced CSV bytes/strings).
        - self.args must expose boolean attributes no_header_row and skip_header (at minimum).
        - self.skip_lines() must return an iterable (or iterator) of rows (each row being a sequence acceptable to agate.csv.reader).
        - agate must be importable and provide agate.csv.reader and agate.csv.writer with the expected interfaces.

    Postconditions (guarantees after successful return):
        - All rows from the input iterable returned by self.skip_lines() have been processed by the writer and written to self.output_file, subject to header transformation rules below.
        - If no exceptions occur, the output stream will contain the same number of data rows as input except where altered by header flags:
            * If no_header_row is True: a synthesized header row (from make_default_headers) appears before the original first row; subsequently, behavior may be modified by skip_header as documented below.
            * If skip_header is True: the first row from the (possibly modified) reader is discarded and not written to output.

## Behavior details and edge cases:
    Reader/Writer initialization:
        - reader is created via: agate.csv.reader(self.skip_lines(), **self.reader_kwargs)
            * reader is expected to be an iterator of row sequences.
        - writer is created via: agate.csv.writer(self.output_file, **self.writer_kwargs)

    no_header_row flag (self.args.no_header_row):
        - When True:
            1. The method advances the reader once to obtain the first existing input row: _row = next(reader).
               - If the input is empty this raises StopIteration.
            2. It computes headers = make_default_headers(len(_row)) to synthesize a header tuple whose length equals the number of columns in the first row.
            3. It reassigns reader to itertools.chain([headers, _row], reader), so the synthesized headers appear as the first row followed by the original first row and the rest.

    skip_header flag (self.args.skip_header):
        - When True:
            - The method calls next(reader) to drop the first row from the current reader and proceeds to write remaining rows.
            - Important interaction with no_header_row: no_header_row processing happens first (synthesizing and prepending headers); then skip_header will drop the new first row (which, if both flags are True, will be the synthesized headers). Combined effect examples:
                * no_header_row=False, skip_header=True:
                    - Drops the original first row from input and writes the rest.
                * no_header_row=True, skip_header=False:
                    - Writes a synthesized header followed by all original rows (first row included).
                * no_header_row=True, skip_header=True:
                    - Synthesizes headers, prepends them, then drops the (synthesized) header row; net effect is that the original first row becomes the first data row written (headers are not emitted).

    Streaming:
        - After optional header handling, writer.writerows(reader) consumes the (possibly chained) reader and writes rows to the output. The reader may be lazily consumed; large inputs are streamed rather than fully materialized.

## Side Effects:
    - Writes to sys.stderr:
        - If self.additional_input_expected() returns True, a diagnostic message is written to stderr:
          "No input file or piped data provided. Waiting for standard input:\n"
    - Writes to external output_file:
        - The method causes agate.csv.writer to write CSV data to self.output_file.
    - No mutation of the CSVFormat object's attributes.

## Implementation notes for re-implementation:
    - Use iterable chaining (itertools.chain) to prepend the synthesized header and original first row when synthesizing headers.
    - Be careful to perform the no_header_row step before skip_header so the documented interaction behavior is reproduced.
    - Ensure exceptions from next(reader) are allowed to propagate (or catch them if you want to provide user-friendly error messages at a higher layer).
    - Validate that writer and reader kwargs are forwarded exactly as supplied in self.reader_kwargs and self.writer_kwargs.

## `csvkit.utilities.csvformat.launch_new_instance` · *function*

## Summary:
Instantiate the CSVFormat CLI utility and delegate execution to its run() method, providing a single-step bootstrap entry point.

## Description:
- Known callers and typical context:
  - Intended to be used as a module-level entry point that external runners, packaging entry_points (for example, console_scripts), or tests can import and call to start the csvformat utility. There are sibling utilities in the repository that expose identical launch_new_instance functions for the same purpose.
  - No internal callers are required; this function is a small adapter to programmatically start the CSVFormat utility.

- Responsibility boundary:
  - This function's sole responsibility is construction of a CSVFormat instance and invoking its run() method. It does not perform argument parsing, CSV processing, or I/O itself; those responsibilities belong to CSVFormat and the surrounding CLI framework. Consult the CSVFormat component documentation for details on command-line flags, I/O behavior, and possible runtime errors originating from the utility.

## Args:
- None. The function accepts no parameters.

## Returns:
- None. The function does not return a value; any observable effects result from CSVFormat.run(). If CSVFormat.run completes normally, the function returns implicitly. If CSVFormat.run raises an exception or calls sys.exit, the function will not return normally.

## Raises:
- NameError
  - Condition: CSVFormat is not defined or not importable in the module namespace when attempting to instantiate it.
- Any exception raised by CSVFormat.__init__
  - Condition: the CSVFormat constructor raises during instantiation; the exception propagates unchanged.
- Any exception raised by CSVFormat.run
  - Condition: runtime errors, including but not limited to parsing or I/O errors, or explicit process termination (SystemExit). These exceptions propagate unchanged.

## Constraints:
- Preconditions:
  - The CSVFormat symbol must be defined and importable in the same module before calling this function.
  - Any runtime context required by CSVFormat.run (for example, command-line arguments in sys.argv or availability of input streams) should be prepared by the caller; this function does not prepare or validate runtime context.
- Postconditions:
  - If the function returns normally, CSVFormat.run has completed without raising an exception that escaped to the caller.
  - No return value is provided; side effects performed by CSVFormat.run (if any) have already occurred.

## Side Effects:
- This function itself performs no I/O. All side effects are those performed by CSVFormat.run and may include I/O, logging, process exit, and exception propagation. This function does not catch or transform exceptions raised by the utility.

## Control Flow:
flowchart TD
    A[Call launch_new_instance()] --> B[Instantiate CSVFormat()]
    B --> C{Instantiation succeeds?}
    C -- no --> D[Constructor exception propagates (function does not handle it)]
    C -- yes --> E[Call CSVFormat.run()]
    E --> F{run() completes normally?}
    F -- no --> G[Runtime exception or SystemExit propagates]
    F -- yes --> H[Function returns None]

## Examples:
- Typical packaging (conceptual):
  - Register csvkit.utilities.csvformat:launch_new_instance as a console_scripts entry point so the packaging runner imports and calls it to start the utility.

- Programmatic invocation with error handling:
  - Use a try/except wrapper if your caller must handle or log initialization/runtime failures rather than letting them propagate:
      try:
          launch_new_instance()
      except Exception as exc:
          # Log or transform the exception, then re-raise or handle
          raise

Notes:
- For details about what CSVFormat.run does (available CLI options, CSV I/O behavior, and specific exceptions that can originate from the utility), refer to the CSVFormat component documentation. This function intentionally remains a minimal bootstrap and does not duplicate CSVFormat's responsibilities.

