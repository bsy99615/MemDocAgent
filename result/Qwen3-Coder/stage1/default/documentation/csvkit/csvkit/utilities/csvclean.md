# `csvclean.py`

## `csvkit.utilities.csvclean.CSVClean` · *class*

## Summary:
A CSV validation and cleaning utility that fixes common formatting errors by checking row lengths against column headers and handling malformed rows.

## Description:
The CSVClean class is a command-line utility that validates CSV data by ensuring row lengths match column headers and attempts to fix common formatting issues such as internal line breaks that cause rows to be split across multiple lines. It extends CSVKitUtility to provide standardized command-line interface handling while using RowChecker for core validation logic.

This utility is particularly useful when processing CSV data that may have been exported from applications that don't strictly enforce CSV formatting rules. It offers both dry-run mode for previewing changes and normal mode for actually cleaning and writing corrected data to files.

## State:
- args: argparse.Namespace containing parsed command-line arguments including the dryrun flag
- output_file: file-like object for writing output messages (typically sys.stdout)
- input_file: file-like object for reading input CSV data (can be sys.stdin or file handle)
- reader_kwargs: dict of keyword arguments for configuring CSV reader construction
- writer_kwargs: dict of keyword arguments for configuring CSV writer construction
- override_flags: list of flag characters to exclude from argument parsing ('L', 'blanks', 'date-format', 'datetime-format')

## Lifecycle:
- Creation: Instantiated by the CSVKit framework during command-line argument parsing
- Usage: Called via the run() method inherited from CSVKitUtility, which executes main() 
- Destruction: Automatic cleanup through Python's garbage collection

## Method Map:
```mermaid
flowchart TD
    A[CSVClean.run] --> B[CSVClean.main]
    B --> C{dryrun flag}
    C -->|True| D[RowChecker(reader)]
    D --> E[checker.checked_rows()]
    E --> F[Process errors and joins]
    F --> G[Write to output_file]
    C -->|False| H[RowChecker(reader)]
    H --> I[checker.checked_rows()]
    I --> J[Write clean data to _out.csv]
    J --> K{errors exist?}
    K -->|Yes| L[Write errors to _err.csv]
    L --> M[Write error count to output_file]
    K -->|No| N[Write "No errors." to output_file]
    M --> O[Write join stats to output_file]
    N --> O
    O --> P[Return]
```

## Raises:
- NotImplementedError: Inherited from CSVKitUtility parent class when add_arguments or main methods aren't properly implemented
- ValueError: Inherited from CSVKitUtility when skip_lines argument is not an integer
- UnicodeDecodeError: Handled by CSVKitUtility's custom exception handler for encoding issues

## Example:
```python
# Dry-run mode (preview only)
# Command: python csvclean.py -n input.csv
# Output to stderr: Line 5: Missing column values
#                   2 rows would have been joined/reduced to 1 rows after eliminating expected internal line breaks.

# Normal mode (actual cleaning)
# Command: python csvclean.py input.csv
# Creates: input_out.csv (cleaned data) and input_err.csv (error log if errors exist)
# Output to stdout: 3 errors logged to input_err.csv
#                   2 rows were joined/reduced to 1 rows after eliminating expected internal line breaks.
```

### `csvkit.utilities.csvclean.CSVClean.add_arguments` · *method*

## Summary:
Adds a dry-run command-line argument to enable preview mode without creating output files.

## Description:
Configures the argument parser to accept a dry-run flag that prevents the creation of output files. When enabled, the utility will analyze the input CSV and report potential errors and row join operations to stderr without writing any modified data to disk.

## Args:
    self: The CSVClean instance containing the argument parser to modify

## Returns:
    None: This method modifies the instance's argument parser in-place

## Raises:
    None: This method does not raise exceptions directly

## State Changes:
    Attributes READ: 
        - self.argparser: The argument parser instance to modify
    
    Attributes WRITTEN:
        - self.argparser: Modified with the new dry-run argument

## Constraints:
    Preconditions:
        - self.argparser must be initialized (typically happens during CSVKitUtility.__init__)
        - The method should be called during the argument parsing setup phase
        
    Postconditions:
        - The argument parser will recognize '-n' or '--dry-run' flags
        - The parsed arguments will contain a 'dryrun' attribute set to True when flag is present

## Side Effects:
    None: This method only modifies the argument parser configuration and has no external I/O or state changes

### `csvkit.utilities.csvclean.CSVClean.main` · *method*

## Summary:
Validates and cleans CSV data by checking row lengths against column headers and optionally writing cleaned output to files.

## Description:
The main method of the CSVClean utility processes CSV input to validate row structures and clean data. In dry-run mode, it identifies validation errors without modifying files. In normal mode, it writes cleaned CSV data to an output file and logs errors to a separate error file when issues are detected. This method handles both standard input and file-based input, creating appropriately named output files.

This method serves as the core processing entry point for the csvclean utility, providing both validation and data cleaning capabilities while maintaining compatibility with standard input/output streams. It separates validation logic from data processing to enable dry-run testing before actual file modification.

## Args:
    self: The CSVClean instance containing CSV processing configuration and state

## Returns:
    None: This method performs I/O operations and does not return a value

## Raises:
    None explicitly raised: All exceptions are handled internally by the underlying CSV processing infrastructure

## State Changes:
    Attributes READ:
        - self.additional_input_expected(): Checks if input is expected
        - self.skip_lines(): Skips initial lines from input
        - self.reader_kwargs: Configuration for CSV reader creation
        - self.args.dryrun: Flag indicating dry-run mode
        - self.input_file: Input file handle (sys.stdin or file handle)
        - self.output_file: Output file handle
        - self.writer_kwargs: Configuration for CSV writer creation
    
    Attributes WRITTEN:
        - self.output_file: Writes validation results, error counts, and join statistics

## Constraints:
    Preconditions:
        - Input file or stdin must be available for processing
        - CSV reader and writer configurations must be properly set up
        - Output directory must be writable
    
    Postconditions:
        - In dry-run mode: Error messages and join statistics written to output file
        - In normal mode: Cleaned CSV written to {base}_out.csv and errors to {base}_err.csv if applicable
        - When input is stdin, output files use 'stdin' as base name (Windows-compatible)

## Side Effects:
    - Reads from standard input or input file handle
    - Writes to output file handle
    - Creates new files with "_out.csv" and "_err.csv" suffixes
    - May write diagnostic messages to stderr when no input is provided
    - File creation and writing operations on disk

### `csvkit.utilities.csvclean.CSVClean._format_error_row` · *method*

## Summary:
Formats a validation error object into a row structure suitable for CSV output, including line number, error message, and the original row data.

## Description:
This method transforms a validation error object into a list format that can be written to a CSV file. It's used in the CSVClean utility to create error reports when CSV validation fails. The method extracts key information from the error object and combines it with the original problematic row data to create a comprehensive error record.

The method is separated from the main logic to maintain clean separation of concerns, allowing the error reporting functionality to be easily tested and modified independently from the core CSV processing logic.

## Args:
    error: An error object containing validation failure information with the following attributes:
        - line_number (int): The line number where the error occurred
        - msg (str): A descriptive error message
        - row (list): The original CSV row data that caused the validation error

## Returns:
    list: A list containing [line_number, msg] followed by all elements from the original row data, formatted for CSV output

## Raises:
    AttributeError: If the error object lacks required attributes (line_number, msg, or row)

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The error parameter must be an object with line_number, msg, and row attributes
    - The row attribute must be iterable (list-like)
    
    Postconditions:
    - The returned list will contain exactly 2 + len(error.row) elements
    - The first two elements will be the line number and error message as strings/integers

## Side Effects:
    None

## `csvkit.utilities.csvclean.launch_new_instance` · *function*

## Summary:
Creates and executes a CSVClean utility instance to validate and clean CSV data.

## Description:
This function serves as the entry point for launching the csvclean command-line utility. It instantiates a CSVClean class and invokes its run method to process CSV data according to the configured command-line arguments. The function abstracts away the instantiation and execution details, providing a clean interface for the csvkit framework to initialize and run the CSV cleaning utility.

This function is part of the standard csvkit utility pattern where each command-line tool has a launch_new_instance function that creates and runs the appropriate utility class instance.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised by this function, though underlying exceptions may propagate from CSVClean.run()

## Constraints:
    Preconditions:
    - The csvkit command-line environment must be properly initialized
    - Command-line arguments must be available for parsing by CSVClean
    - Standard input/output streams must be accessible
    
    Postconditions:
    - The CSVClean utility will have processed input CSV data according to its configuration
    - Output will be written to either stdout/stderr or specified output files
    - The process will exit with appropriate status codes based on processing results

## Side Effects:
    - Reads from standard input or specified input file(s)
    - Writes to standard output or specified output file(s)
    - May create additional output files (e.g., _out.csv, _err.csv) based on processing results
    - May write diagnostic messages to standard error
    - Processes command-line arguments through the csvkit argument parser

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance called] --> B[Create CSVClean instance]
    B --> C[Call utility.run()]
    C --> D{CSVClean.run executes}
    D --> E[CSVClean.main processes CSV data]
    E --> F{Dry-run mode?}
    F -->|Yes| G[Validate rows, report errors]
    G --> H[Write validation results to stderr]
    F -->|No| I[Clean and write data to _out.csv]
    I --> J{Errors detected?}
    J -->|Yes| K[Write error log to _err.csv]
    K --> L[Write error count to stdout]
    J -->|No| M[Write success message to stdout]
    L --> N[Return]
    M --> N
    H --> N
```

## Examples:
```python
# Typical usage from command line:
# python csvclean.py input.csv

# Or with dry-run mode:
# python csvclean.py -n input.csv

# The launch_new_instance function is automatically called by the csvkit framework
# when the csvclean utility is invoked, handling the instantiation and execution
# of the CSVClean utility class internally.
```

