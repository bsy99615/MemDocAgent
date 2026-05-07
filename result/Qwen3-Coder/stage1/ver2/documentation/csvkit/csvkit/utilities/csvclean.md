# `csvclean.py`

## `csvkit.utilities.csvclean.CSVClean` · *class*

*No documentation generated.*

### `csvkit.utilities.csvclean.CSVClean.add_arguments` · *method*

## Summary:
Adds a command-line argument for enabling dry-run mode that prevents output file creation.

## Description:
This method configures the argument parser to accept a `-n`/`--dry-run` flag that, when specified, prevents the utility from creating output files. Instead, information about what would have been done is printed to standard error.

This logic is separated into its own method to follow the CSVKitUtility pattern where each subclass implements its own `add_arguments()` method to define custom command-line options while inheriting common CSV processing arguments from the base class.

## Args:
    self: The CSVClean instance

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self.argparser
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The method assumes self.argparser exists and is an argparse.ArgumentParser instance
    Postconditions: The argument parser will recognize the -n/--dry-run flag

## Side Effects:
    None

### `csvkit.utilities.csvclean.CSVClean.main` · *method*

## Summary:
Processes CSV data to validate and clean rows, reporting errors and optionally creating cleaned output files.

## Description:
The main method of the CSVClean utility that performs CSV validation and cleaning operations. It operates in two modes: dry-run mode (validates only) and normal processing mode (validates and cleans). In dry-run mode, it analyzes CSV data for errors without creating output files. In normal mode, it cleans CSV data by joining incomplete rows, writes the cleaned data to a new file, and logs validation errors to a separate error file.

This method is called during the execution lifecycle of the CSVClean utility, typically after argument parsing and file initialization have completed. It serves as the core processing engine that transforms raw CSV input into validated, cleaned output while providing detailed feedback about data quality issues.

## Args:
    self: The CSVClean instance containing command-line arguments, input/output file handles, and CSV processing configuration.

## Returns:
    None: This method performs I/O operations and does not return a value.

## Raises:
    None explicitly raised by this method. Exceptions from underlying operations (CSV parsing, file I/O) are handled by the parent CSVKitUtility class.

## State Changes:
    Attributes READ:
        - self.args.dryrun: Boolean flag determining processing mode
        - self.args.input_path: Command-line argument specifying input file path
        - self.input_file: File handle for input CSV data
        - self.output_file: File handle for output messages
        - self.reader_kwargs: Configuration for CSV reader creation
        - self.writer_kwargs: Configuration for CSV writer creation
    Attributes WRITTEN:
        - self.output_file: Written to for status messages and error reports

## Constraints:
    Preconditions:
        - self.args must be properly initialized (after argument parsing)
        - self.input_file must be opened and accessible
        - self.output_file must be writable
        - CSVKitUtility's skip_lines() method must have been called to position input file correctly
        
    Postconditions:
        - Error messages are written to self.output_file
        - In normal mode, cleaned CSV data is written to {base}_out.csv where base is input filename or 'stdin'
        - In normal mode, error details are written to {base}_err.csv if errors exist
        - File handles remain open for proper cleanup by parent class

## Side Effects:
    - Writes to stderr when waiting for standard input (when additional_input_expected returns True)
    - Creates new files with "_out.csv" and "_err.csv" suffixes in the same directory as input
    - Performs file I/O operations on input and output streams
    - May write to stdout/stderr via self.output_file handle

### `csvkit.utilities.csvclean.CSVClean._format_error_row` · *method*

## Summary:
Formats a CSV validation error into a structured row for error logging.

## Description:
Converts a CSVTestException error object into a list format suitable for writing to an error log CSV file. This method extracts the line number, error message, and original row data from the error object to create a standardized error report row.

The method is called during CSV cleaning operations when validation errors are detected. It's used to prepare error information for output to a separate error log file, allowing users to identify and address problematic rows in their CSV data.

## Args:
    error (CSVTestException): A validation error object containing line_number, msg, and row attributes.

## Returns:
    list: A list containing [line_number, msg] followed by all elements from error.row.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: error.line_number, error.msg, error.row
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The error parameter must be a CSVTestException object with line_number, msg, and row attributes.
    Postconditions: The returned list will contain exactly len(error.row) + 2 elements.

## Side Effects:
    None.

## `csvkit.utilities.csvclean.launch_new_instance` · *function*

## Summary:
Launches a new instance of the CSVClean utility to fix common errors in CSV files.

## Description:
This function serves as the primary entry point for executing the csvclean command-line utility. It creates a new instance of the CSVClean class and invokes its run method to process CSV data according to command-line arguments. This follows the standard pattern used by all csvkit utilities for launching command-line tools.

The CSVClean utility identifies and fixes common CSV formatting issues including malformed lines, unexpected line breaks, and other structural problems that can occur in CSV data. It can operate in two modes: dry-run mode (which analyzes files without creating output) or normal mode (which produces cleaned output files).

## Args:
    None

## Returns:
    None

## Raises:
    SystemExit: Raised by the underlying CSVKitUtility.run() method when command-line arguments are invalid or when processing completes successfully
    IOError: Raised by file I/O operations when reading input files or writing output files fails
    csv.Error: Raised by CSV parsing when malformed CSV data is encountered
    MemoryError: Raised when insufficient memory is available for processing large CSV files

## Constraints:
    Preconditions:
    - Command-line arguments must be available in sys.argv for parsing
    - Input files must be readable and output directories must be writable
    - Environment must support file system operations
    
    Postconditions:
    - The function executes the complete CSV cleaning workflow
    - Either processes input CSV files and generates output/error files, or displays diagnostic information
    - Function does not return any meaningful value

## Side Effects:
    - Parses command-line arguments from sys.argv
    - Reads input CSV files from disk or stdin
    - Writes processed CSV data to output files (filename_out.csv)
    - Writes error information to separate error log files (filename_err.csv) when errors are detected
    - Writes diagnostic information to stderr (when --dry-run is used or when no input is provided)
    - May create new files in the working directory
    - May modify the global sys.argv state through argument parsing

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance called] --> B[Create CSVClean instance]
    B --> C[Call utility.run()]
    C --> D{Argument parsing complete}
    D --> E{Input expected?}
    E -->|No| F[Display waiting message to stderr]
    E -->|Yes| G[Open input file or stdin]
    G --> H{Dry-run mode?}
    H -->|Yes| I[Parse CSV, check rows, report errors to stderr]
    H -->|No| J[Open output file for writing]
    J --> K[Write cleaned data to output file]
    K --> L{Errors detected?}
    L -->|Yes| M[Create error log file]
    M --> N[Write error details to log file]
    N --> O[Report error count to stdout]
    L -->|No| P[Report "No errors" to stdout]
    I --> Q[End]
    P --> Q
    O --> Q
```

## Examples:
```python
# Launches csvclean utility with default settings
# This is typically called internally by the csvclean command
launch_new_instance()

# Typical command-line usage (which internally calls this function):
# csvclean input.csv

# Dry-run mode (analyzes without modifying files):
# csvclean -n input.csv

# With custom delimiter:
# csvclean -d ';' input.csv
```

