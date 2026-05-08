# `in2csv.py`

## `csvkit.utilities.in2csv.In2CSV` · *class*

*No documentation generated.*

### `csvkit.utilities.in2csv.In2CSV.add_arguments` · *method*

## Summary:
Registers and configures all command-line arguments used by the In2CSV utility by adding them to the instance's argument parser, mutating its state so subsequent parser.parse_args() will recognize the In2CSV options.

## Description:
This method is invoked during CLI setup by the CSVKit CLI framework (the CSVKitUtility-based bootstrap) as part of the utility's parser construction phase, before command-line arguments are parsed and before main execution. Its purpose is to keep all argument registration in one place so the parser-building logic is separated from argument-handling and run-time logic; this improves readability, testability, and reuse of argument specifications.

Known callers / invocation context:
- The CLI bootstrap that constructs an In2CSV instance (the CSVKitUtility-driven entry sequence) calls this method while preparing the argparse.ArgumentParser. It is expected to be run once per In2CSV instance prior to parsing args.

Why this is a separate method:
- Centralizes the CLI option definitions for In2CSV.
- Allows other parts of the framework to inspect or modify the parser before parsing.
- Simplifies unit testing of argument registration and documentation generation.

## Args:
This method takes no parameters.

The method registers the following command-line arguments (each line describes the CLI flag(s), the destination attribute on self.args, type and default):

- Positional: FILE
  - dest: input_path
  - type: str (path or '-' for stdin)
  - nargs: optional (nargs='?')
  - default: None (absent)
  - Description: The input file to operate on. If omitted or '-' the utility expects piped data from STDIN.

- -f, --format
  - dest: filetype
  - type: str
  - allowed values: the iterable SUPPORTED_FORMATS (module-level constant)
  - default: None
  - Description: Explicitly specify input file format; if omitted the format is inferred.

- -s, --schema
  - dest: schema
  - type: str (path to a CSV-formatted schema file)
  - default: None
  - Description: Schema file used for converting fixed-width files.

- -k, --key
  - dest: key
  - type: str
  - default: None
  - Description: Top-level key to select a list of objects within JSON input.

- -n, --names
  - dest: names_only
  - type: bool (action='store_true')
  - default: False
  - Description: When set, prints sheet names from an Excel input and exits.

- --sheet
  - dest: sheet
  - type: str (sheet name or numeric string)
  - default: None
  - Description: Select the Excel sheet to operate on.

- --write-sheets
  - dest: write_sheets
  - type: str
  - default: None
  - Description: Comma-separated sheet names or indices to write to separate CSV files; the special value "-" writes all sheets.

- --use-sheet-names
  - dest: use_sheet_names
  - type: bool (action='store_true')
  - default: False
  - Description: When writing multiple sheets to files, use the sheet names for file names instead of numeric indices.

- --encoding-xls
  - dest: encoding_xls
  - type: str
  - default: None
  - Description: Encoding override for legacy .xls files when reading with xlrd/agate.

- -y, --snifflimit
  - dest: sniff_limit
  - type: int
  - default: 1024
  - Description: Limit (in bytes) for CSV dialect sniffing. Special values:
      - 0: disable sniffing entirely
      - -1: sniff the entire file (interpreted by caller as None)

- -I, --no-inference
  - dest: no_inference
  - type: bool (action='store_true')
  - default: False
  - Description: Disable type inference when parsing CSV input (also suppresses --locale, --date-format, --datetime-format behavior).

## Returns:
- None. The method returns implicitly (None) after mutating self.argparser by registering the listed options.

## Raises:
- Exceptions raised by the underlying argparse implementation (e.g., argparse.ArgumentError, ValueError) may propagate if:
    - An option is added twice (duplicate option strings or conflicting destinations).
    - SUPPORTED_FORMATS is not a valid iterable for the 'choices' parameter.
  These are not explicitly raised by this method; they are side effects of invalid usage of argparse.add_argument.

## State Changes:
Attributes READ:
- self.argparser (reads to call add_argument)
- SUPPORTED_FORMATS (module-level constant referenced for choices)

Attributes WRITTEN (mutated):
- self.argparser — mutated by multiple calls to add_argument; after the call the parser recognizes new options whose values will be available on self.args after parsing.

No other self.* attributes are read or modified by this method.

## Constraints:
Preconditions:
- self.argparser must be an argparse.ArgumentParser-like object exposing add_argument(...) method that accepts the parameters used here.
- SUPPORTED_FORMATS must exist in module scope and be an iterable of valid string choices (or None will cause argparse to complain).
- This method should be called prior to parser.parse_args(); calling it after parsing or repeatedly may raise errors from argparse.

Postconditions:
- The instance's argument parser includes the configured options and will produce self.args attributes with the specified dest names when parse_args() is invoked.
- The defaults described above (sniff_limit=1024; boolean flags default False; unspecified strings default None) will be in effect unless overridden by argparse or previous parser configuration.

## Side Effects:
- Mutates the argument parser (self.argparser) by registering multiple command-line options.
- No I/O is performed by this method.
- No network or file-system side effects occur.
- Potential exceptions from argparse.add_argument may be raised and will propagate to the caller.

### `csvkit.utilities.in2csv.In2CSV.open_excel_input_file` · *method*

## Summary:
Return an open, readable binary stream for an Excel input source: either a BytesIO wrapping all data read from STDIN (when path is None, empty, or '-') or a file object opened in binary mode for the provided filesystem path. The returned stream is intended to be assigned to self.input_file for downstream Excel-reading routines.

## Description:
Known callers and context:
- sheet_names(path, filetype): Calls this method early when only sheet names are required; the returned stream is read (possibly fully) and then closed by the caller.
- main(): Calls this when filetype is 'xls' or 'xlsx' to populate self.input_file before feeding it to agate's Excel readers; main also re-calls this when writing multiple sheets (after closing a previously-opened input_file).

Lifecycle stage:
- This method is invoked during input setup in the utility's main pipeline: it centralizes the logic for obtaining a binary stream from either STDIN or a filesystem path before any format-specific parsing is performed.

Why this is a separate method:
- It encapsulates the single responsibility of producing a consistent binary file-like object regardless of whether input comes from STDIN or a file path. Centralizing this logic prevents duplication where multiple code paths (sheet inspection, main processing, write-sheets re-open) need identical stdin-vs-file handling and makes it easier to reason about close semantics and stream type.

## Args:
    path (str | os.PathLike | None): Path to the input file on disk, or '-' to indicate STDIN. If path is None or the empty string, it is treated the same as '-'. There is no default value — callers pass whatever they obtained from CLI parsing.

## Returns:
    file-like object (binary):
    - If path is falsy (None, '' ) or exactly '-', returns io.BytesIO containing the full contents read from sys.stdin.buffer. The BytesIO is positioned at the start (ready for reading).
    - Otherwise, returns a binary file object opened with open(path, 'rb') (typically an instance providing read(), close(), and, on many platforms, a name attribute).
    Edge cases:
    - If STDIN is empty, the method returns an empty BytesIO.
    - The returned object may or may not have a .name attribute; callers that require .name (e.g., DBF handling) must validate its presence.

## Raises:
    - FileNotFoundError: propagated from open(path, 'rb') if the filesystem path does not exist.
    - PermissionError: propagated from open(path, 'rb') if the file is not readable due to permissions.
    - OSError (other I/O errors): any underlying I/O error from open() is propagated.
    - AttributeError: if sys.stdin has no 'buffer' attribute in the current environment, accessing sys.stdin.buffer will raise AttributeError (this is possible in unusual embeded runtimes). This exception is propagated.
    Notes:
    - The method does not catch or transform these exceptions; callers must handle them if needed.

## State Changes:
    Attributes READ:
    - None (the method reads no attributes from self)

    Attributes WRITTEN:
    - None (the method does not modify any self.<attr> attributes)

## Constraints:
    Preconditions:
    - The caller should pass a path that is str or os.PathLike, or pass '-'/None to indicate STDIN.
    - When indicating STDIN, callers must be prepared for the method to consume (read) all remaining stdin data — this is destructive and cannot be undone.
    - Callers that require an underlying filename (e.g., DBF conversion which checks for self.input_file.name) must not pass '-' or None because the returned BytesIO will lack a stable filesystem name.

    Postconditions:
    - The method returns a readable, binary file-like object positioned at the start.
    - No attributes on self are modified by this call.
    - The caller is responsible for closing the returned object when finished (the method does not close it).

## Side Effects:
    - I/O:
        - If reading from STDIN, the method reads all remaining bytes from sys.stdin.buffer, consuming the stream.
        - If given a filesystem path, the method opens that file for binary reading, which involves filesystem access and leaves an open file descriptor until the caller closes it.
    - No network calls or external services are invoked.
    - The method itself performs no cleanup (closing); callers must close the returned stream to free resources.

## Implementation notes for reimplementation:
    - Use sys.stdin.buffer.read() to obtain raw bytes from STDIN, then wrap them in io.BytesIO and return that BytesIO instance.
    - For disk paths, use open(path, 'rb') and return the file object directly.
    - Do not swallow exceptions from open() or stdin access; allow them to propagate so callers can handle errors in a centralized place (as main() currently does via CLI error handling).

### `csvkit.utilities.in2csv.In2CSV.sheet_names` · *method*

## Summary:
Return the list of sheet names from an Excel workbook (XLS or XLSX) opened from the given path; closes the opened input file before returning on the happy path.

## Description:
Known callers and context:
    - Called from In2CSV.main when the CLI is invoked with --names / -n to list sheet names from an Excel file.
    - Called from In2CSV.main when --write-sheets is "-" to obtain all sheet names to write each sheet to a separate CSV file.
    - Lifecycle stage: invoked early in the conversion pipeline when the tool needs to enumerate sheets without constructing agate tables for each sheet.

Why this is a separate method:
    - Centralizes logic for opening Excel input and selecting the appropriate backend (xlrd for 'xls', openpyxl for 'xlsx'), avoiding duplication where multiple CLI flags require sheet enumeration.
    - Encapsulates backend-specific read semantics (reading all bytes for xlrd vs. delegating a file-like to openpyxl), so callers receive a simple list-of-names API.

## Args:
    path (str or None):
        Path to the Excel file to open. If None or '-' the method will read from STDIN via self.open_excel_input_file, which returns a BytesIO over stdin bytes.
    filetype (str):
        Expected Excel file format. Recognized values:
            - 'xls': treat as legacy Excel (use xlrd)
            - 'xlsx': treat as modern Excel (use openpyxl)
        Behavior: if filetype == 'xls' xlrd is used; otherwise (any other value) the method uses openpyxl. Callers in this codebase pass only 'xls' or 'xlsx'.

## Returns:
    list[str]:
        A list of sheet name strings in workbook order. May be an empty list if the workbook contains no sheets. On normal (non-exceptional) exit the input file returned by open_excel_input_file has been closed.

## Raises:
    Propagates exceptions from lower-level operations. Examples include but are not limited to:
        - FileNotFoundError: if a concrete path is given and opening the file fails.
        - Exceptions raised by self.open_excel_input_file when reading STDIN or opening the path.
        - xlrd-specific errors (e.g., xlrd.biffh.XLRDError) when filetype == 'xls' and the bytes are not a valid XLS.
        - openpyxl-related exceptions (for example openpyxl.utils.exceptions.InvalidFileException or zipfile.BadZipFile) when filetype is treated as 'xlsx' and the file is not a valid XLSX archive.
    Note: this method does not catch these exceptions; they propagate to the caller.

## State Changes:
Attributes READ:
    - None of the object's attributes are read or mutated by this method. The method does call the instance method self.open_excel_input_file(path), but does not read self.<attribute> fields.

Attributes WRITTEN:
    - None. The method uses only local variables and closes the local file-like object before returning on the normal path.

## Constraints:
Preconditions:
    - self.open_excel_input_file(path) must return a file-like object supporting read() and close() (the implemented open_excel_input_file returns a BytesIO or an opened file object).
    - The caller should pass a filetype that reflects the actual file format ('xls' or 'xlsx'); otherwise the wrong parser will be used and parsing will likely fail.

Postconditions:
    - If the method returns normally (no exception), the opened input file will have been closed and the returned value is a list of sheet names.
    - If an exception is raised while loading the workbook (before the explicit input_file.close() call), the input_file may remain unclosed because the method does not use a finally/with block to guarantee closure.

## Side Effects:
    - Performs I/O: opens the file at path (or reads stdin into a BytesIO) and passes bytes or a file-like object to the Excel backend.
    - Memory behavior:
        - For filetype == 'xls': the method calls input_file.read() and passes the bytes to xlrd.open_workbook(file_contents=...), which reads the entire file into memory; large XLS files will consume memory proportional to file size.
        - For filetype != 'xls' (treated as 'xlsx'): the method passes the file-like object to openpyxl.load_workbook with read_only=True and data_only=True; openpyxl may stream-read in read-only mode, reducing peak memory compared with reading all bytes at once.
    - Resource management: the method closes the input file on the successful path; however, if an exception occurs during workbook loading, the file may not be closed by this method.

### `csvkit.utilities.in2csv.In2CSV.main` · *method*

*No documentation generated.*

## `csvkit.utilities.in2csv.launch_new_instance` · *function*

## Summary:
Create a fresh In2CSV instance and start its execution lifecycle by invoking its run() method.

## Description:
- Known callers within the provided codebase:
    - No explicit callers were found in the provided source context. This function is typically used as a thin top-level entry point (for example, a console-script or module-level entry invoked by if __name__ == '__main__') that starts the In2CSV command lifecycle.

- Responsibility boundary:
    - This function exists solely to construct the In2CSV command object and transfer control to its run() method. It does not perform parsing, I/O, or business logic itself — all operational work is performed by the In2CSV instance it creates.
    - Extracting this small helper into its own function centralizes the CLI entrypoint logic (instantiation + run) so packaging tools (setuptools entry_points) or tests can reference a simple callable.

## Args:
    None

## Returns:
    None
    - This function does not return a value. It delegates to In2CSV.run(); any return value from that method (if any) is not captured or returned by launch_new_instance.

## Raises:
    - Any exception raised by In2CSV.__init__ will propagate out of this function.
    - Any exception raised by In2CSV.run() will propagate out of this function.
    - This function contains no try/except; callers should expect exceptions from the underlying class constructor or run invocation.

## Constraints:
- Preconditions:
    - The name In2CSV must be defined and importable in the module scope where this function is defined.
    - The environment expected by In2CSV.__init__ and In2CSV.run (command-line state, modules, etc.) must be prepared by the caller or by module-level initialization.

- Postconditions:
    - If this function returns normally, it means In2CSV.run() completed without raising an exception.
    - If an exception is raised, no cleanup is performed by launch_new_instance itself; any required cleanup is the responsibility of In2CSV.run() or its internals.

## Side Effects:
- Indirect: All side effects originate from In2CSV.__init__ and In2CSV.run(). Those may include (but are not performed by this function directly):
    - Opening/reading/writing files, network or stdout/stderr I/O.
    - Modifying global or module-level state if In2CSV or its run() implementation does so.
    - Emitting warnings or altering warning filter state (if implemented by In2CSV.run()).
- Direct: allocation of an In2CSV instance and a direct call to its run() method.

## Control Flow:
flowchart TD
    A[Start: call launch_new_instance] --> B[Call In2CSV()]
    B --> C{In2CSV.__init__ raises?}
    C -- Yes --> D[Exception propagates out of launch_new_instance]
    C -- No --> E[Call utility.run() on the created instance]
    E --> F{utility.run() completes normally?}
    F -- Yes --> G[launch_new_instance returns None]
    F -- No --> H[Exception propagates out of launch_new_instance]

## Examples:
- Typical usage as a module-level entrypoint:
    - In a packaging entry point or a top-level script, use this function to start the command:
        try:
            launch_new_instance()
        except Exception as e:
            # handle or log fatal error (the function does not handle exceptions itself)
            sys.exit(1)

- In tests, call directly to exercise the full CLI lifecycle (tests should set up any required environment, CLI args, or monkeypatch In2CSV internals to avoid real I/O).

