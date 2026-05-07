# `csvclean.py`

## `csvkit.utilities.csvclean.CSVClean` · *class*

## Summary:
CSVClean is a command-line utility that fixes common errors in CSV files by validating row lengths, handling multi-line fields, and producing cleaned output files.

## Description:
CSVClean addresses common CSV formatting issues such as inconsistent row lengths, malformed multi-line fields, and other structural problems that can occur in CSV data. It operates in two modes: dry-run mode for error detection without creating output files, and normal mode for actually cleaning and writing corrected CSV data. The utility leverages the RowChecker class to validate CSV structure and automatically fix certain issues like joining rows that appear to be split due to embedded newlines.

This class is part of the csvkit suite and inherits standard CSV processing capabilities from CSVKitUtility, including argument parsing, file handling, and CSV reader/writer configuration.

## State:
- `argparser`: argparse.ArgumentParser instance inherited from CSVKitUtility for command-line argument parsing
- `args`: Parsed command-line arguments from argparse, including the dryrun flag
- `output_file`: File-like object for writing output (inherited from CSVKitUtility)
- `input_file`: File-like object for reading input (inherited from CSVKitUtility)
- `reader_kwargs`: Dictionary of keyword arguments for CSV reader construction (inherited from CSVKitUtility)
- `writer_kwargs`: Dictionary of keyword arguments for CSV writer construction (inherited from CSVKitUtility)
- `description`: Class variable set to 'Fix common errors in a CSV file.'
- `override_flags`: Class variable set to ['L', 'blanks', 'date-format', 'datetime-format'] to exclude certain command-line options

## Lifecycle:
Creation: Instantiate with optional args list and output_file parameter. The constructor:
1. Initializes the common argument parser from CSVKitUtility
2. Calls add_arguments() to register the --dry-run flag
3. Parses arguments using argparse
4. Sets up output file handle
5. Extracts CSV reader and writer kwargs
6. Installs exception handler
7. Sets up SIGPIPE signal handling

Usage: Call `run()` method which orchestrates the execution flow:
1. Checks if additional input is expected from stdin using additional_input_expected()
2. Skips specified lines using skip_lines() if applicable
3. Creates a CSV reader using agate.csv.reader with reader_kwargs
4. If --dry-run flag is set:
   - Uses RowChecker to validate rows without writing output
   - Reports errors to stderr via output_file
   - Shows row joining statistics
5. If --dry-run flag is not set:
   - Determines output filename based on input file name or stdin
   - Creates cleaned output file with '_out.csv' suffix
   - Writes cleaned data with proper headers using clean_writer
   - If errors are found, creates error log file with '_err.csv' suffix
   - Reports statistics to output file

Destruction: Automatic cleanup occurs through context managers and file closing in the run() method.

## Method Map:
```mermaid
graph TD
    A[run()] --> B[additional_input_expected()]
    B --> C{Additional input expected?}
    C -->|Yes| D[sys.stderr.write()]
    D --> E[skip_lines()]
    E --> F[agate.csv.reader()]
    F --> G{dryrun flag set?}
    G -->|Yes| H[RowChecker(F)]
    H --> I[checker.checked_rows()]
    I --> J{Errors found?}
    J -->|Yes| K[self.output_file.write()]
    J -->|No| L[self.output_file.write()]
    G -->|No| M[splitext(input_file.name)]
    M --> N{input_file == sys.stdin?}
    N -->|Yes| O[base = 'stdin']
    N -->|No| P[base = splitext(input_file.name)[0]]
    P --> Q[open(base + '_out.csv', 'w')]
    Q --> R[agate.csv.writer(Q)]
    R --> S[RowChecker(F)]
    S --> T[clean_writer.writerow(checker.column_names)]
    T --> U[for row in checker.checked_rows(): clean_writer.writerow(row)]
    U --> V{Errors found?}
    V -->|Yes| W[open(error_filename, 'w')]
    W --> X[agate.csv.writer(W)]
    X --> Y[error_writer.writerow(error_header)]
    Y --> Z[for e in checker.errors: error_writer.writerow(_format_error_row(e))]
    Z --> AA[self.output_file.write()]
    V -->|No| AB[self.output_file.write()]
    AB --> AC{Joins detected?}
    AC -->|Yes| AD[self.output_file.write()]
```

## Raises:
- NotImplementedError: Raised by add_arguments() and main() if not overridden by subclasses (inherited from CSVKitUtility)
- RequiredHeaderError: Raised by print_column_names() when --no-header-row is used with -n/--names (inherited from CSVKitUtility)
- ValueError: Raised by skip_lines() when skip_lines argument is not an integer (inherited from CSVKitUtility)
- UnicodeDecodeError: Handled by custom exception handler for encoding issues (inherited from CSVKitUtility)
- LengthMismatchError: Raised by RowChecker when CSV rows have inconsistent column counts
- CSVTestException: Raised by RowChecker for various CSV validation failures

## Example:
```python
# Dry-run mode - validate CSV without creating output files
# python csvclean.py --dry-run input.csv

# Normal mode - clean CSV and create output files
# python csvclean.py input.csv

# With custom output file naming
# python csvclean.py input.csv > output.txt

# Using with piped input
# echo "col1,col2,col3\nval1,val2,val3" | python csvclean.py --dry-run
```

### `csvkit.utilities.csvclean.CSVClean.add_arguments` · *method*

## Summary:
Adds a dry-run command-line argument to control whether output files are created or only diagnostic information is printed.

## Description:
This method extends the command-line argument parser to include a dry-run option that allows users to preview what changes would be made to a CSV file without actually creating output files. When the --dry-run or -n flag is specified, the utility will analyze the input and report errors and row joining operations to STDERR without writing to disk.

## Args:
    self: The CSVClean instance whose argparser will be modified

## Returns:
    None: This method modifies the instance's argparser in-place and returns nothing

## Raises:
    None: This method does not raise exceptions directly

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: Modifies self.argparser by adding a new argument

## Constraints:
    Preconditions: 
    - The method must be called on a CSVClean instance that has an initialized argparser attribute
    - The argparser must be an instance of argparse.ArgumentParser
    
    Postconditions:
    - The argparser will contain a new '--dry-run'/'-n' argument
    - The parsed arguments will include a 'dryrun' attribute that is True when the flag is used, False otherwise

## Side Effects:
    None: This method only modifies the argument parser configuration and has no I/O or external service calls

### `csvkit.utilities.csvclean.CSVClean._format_error_row` · *method*

## Summary:
Formats a validation error object into a structured row for error reporting.

## Description:
Converts a validation error object into a list format suitable for writing to an error CSV file. This method extracts the line number and error message from the error object, then appends the original row data to create a complete error record.

This method is called during CSV cleaning operations when validation errors are detected in input data. It serves as a dedicated formatter to ensure consistent error reporting structure across different types of validation failures handled by the RowChecker class.

## Args:
    error: An error object containing validation failure information with attributes:
        - line_number (int): The line number in the CSV file where the error occurred
        - msg (str): The error message describing the validation failure
        - row (list): The original row data that caused the validation error

## Returns:
    list: A formatted row containing [line_number, msg] followed by the original row data elements

## Raises:
    None explicitly raised by this method

## State Changes:
    Attributes READ: error.line_number, error.msg, error.row
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The error parameter must be an object with line_number, msg, and row attributes
        - The row attribute must be iterable (list-like structure)
    Postconditions:
        - Returns a list with at least two elements (line_number and msg)
        - The returned list contains all elements from the original error row

## Side Effects:
    None

## `csvkit.utilities.csvclean.launch_new_instance` · *function*

## Summary:
Creates and executes a new CSVClean utility instance to process CSV files.

## Description:
This function serves as the entry point for launching the csvclean utility. It instantiates a CSVClean object and invokes its run method to execute the CSV cleaning process. The function encapsulates the basic workflow of creating a utility instance and running it, providing a clean interface for starting the CSV cleaning operation.

The CSVClean utility itself validates CSV structure, handles multi-line fields, and produces cleaned output files while optionally reporting errors. It operates in either dry-run mode (validation only) or normal mode (actual cleaning and file creation). This function is typically called by the csvkit command-line framework when the csvclean command is invoked.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised by this function, though the underlying CSVClean.run() method may raise various exceptions during execution including:
    - NotImplementedError: From CSVKitUtility base class if not properly overridden
    - RequiredHeaderError: When header row requirements are violated
    - ValueError: For invalid skip lines arguments
    - UnicodeDecodeError: For encoding issues
    - LengthMismatchError: When CSV rows have inconsistent column counts
    - CSVTestException: For various CSV validation failures

## Constraints:
    Preconditions:
    - Command-line arguments must be available in sys.argv for parsing
    - Standard CSVKitUtility initialization requirements are met
    - Valid input file paths or stdin availability for CSV processing
    
    Postconditions:
    - A CSVClean utility instance is created and executed
    - Either dry-run validation completes or cleaning operation finishes
    - Output files are created if in normal mode (unless errors occur)

## Side Effects:
    - Reads from standard input or specified input files (via CSVKitUtility)
    - Writes to standard output or specified output files (via CSVKitUtility)
    - May create new files with '_out.csv' and '_err.csv' suffixes
    - Writes error messages to standard error
    - May modify global state through signal handlers and exception handlers installed by CSVKitUtility

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[CSVClean().__init__()]
    B --> C[CSVClean().run()]
    C --> D{CSVClean.run() execution}
    D -->|Success| E[Normal completion]
    D -->|Exception| F[Exception propagated to caller]
```

## Examples:
```python
# Typical usage in command-line context
# This function is typically called internally by csvkit's CLI framework
# when the csvclean command is invoked

# In a programmatic context:
from csvkit.utilities.csvclean import launch_new_instance
launch_new_instance()
```

