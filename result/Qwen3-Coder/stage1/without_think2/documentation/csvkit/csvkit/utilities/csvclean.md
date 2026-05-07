# `csvclean.py`

## `csvkit.utilities.csvclean.CSVClean` · *class*

## Summary:
CSVClean is a command-line utility that identifies and fixes common formatting errors in CSV files, including inconsistent row lengths and embedded line breaks.

## Description:
The CSVClean utility processes CSV input to detect and resolve formatting issues that commonly occur in real-world CSV data. It can operate in two modes: dry-run mode, which analyzes input without creating output files, and normal mode, which creates cleaned output files. The utility leverages RowChecker to validate row consistency and attempt to reconstruct records that span multiple lines due to embedded quotes or line breaks.

This class extends CSVKitUtility, inheriting common CSV processing infrastructure and command-line argument handling. It's designed to be used as a standalone command-line tool for preprocessing CSV data before further analysis or import operations.

## State:
- args: argparse.Namespace containing parsed command-line arguments including the dryrun flag
- output_file: file-like object for writing output messages (default: sys.stdout)
- input_file: file-like object for reading CSV input data
- reader_kwargs: dict of keyword arguments for configuring CSV reader behavior
- writer_kwargs: dict of keyword arguments for configuring CSV writer behavior

## Lifecycle:
- Creation: Instantiate with optional command-line arguments and output file handle
- Usage: Call run() method which orchestrates the complete workflow:
  1. Parse command-line arguments via add_arguments()
  2. Open input file if needed
  3. Execute main() method for CSV processing
  4. Close input file if needed
- Destruction: Automatic cleanup handled by parent CSVKitUtility.run() method

## Method Map:
```mermaid
flowchart TD
    A[CSVClean.run] --> B[CSVClean.add_arguments]
    B --> C[CSVClean.main]
    C --> D{Dry-run mode?}
    D -->|Yes| E[RowChecker(reader)]
    E --> F[checker.checked_rows()]
    F --> G{Errors found?}
    G -->|Yes| H[Write error messages to output_file]
    G -->|No| I[Write "No errors." to output_file]
    D -->|No| J[RowChecker(reader)]
    J --> K[Write header row to output file]
    K --> L[Write cleaned rows to output file]
    L --> M{Errors found?}
    M -->|Yes| N[Create error file with error details]
    N --> O[Write error count to output_file]
    M -->|No| P[Write "No errors." to output_file]
```

## Raises:
- NotImplementedError: Raised by parent CSVKitUtility if add_arguments or main methods are not properly overridden
- ValueError: Raised by skip_lines() when skip_lines argument is not an integer
- RequiredHeaderError: Raised by print_column_names() when --no-header-row is used with -n/--names

## Example:
```python
# Dry-run mode - analyze without creating files
# python csvclean.py -n input.csv

# Normal mode - create cleaned output files
# python csvclean.py input.csv

# With custom output file
# python csvclean.py input.csv > output.txt
```

### `csvkit.utilities.csvclean.CSVClean.add_arguments` · *method*

## Summary:
Configures command-line argument parsing to accept a dry-run flag for CSV cleaning operations.

## Description:
This method adds a command-line argument to the utility's argument parser that enables users to perform a dry run of the CSV cleaning process. During a dry run, the utility analyzes the input CSV file for potential issues without creating any output files. Instead, it reports information about what would have been done to STDERR.

The method is part of the CSVClean class which extends CSVKitUtility, and it's called during the initialization phase of the command-line utility setup. This logic is separated into its own method to maintain clean separation of concerns and allow for easy extension of argument parsing in the future.

## Args:
    self: The instance of the CSVClean class containing the argparser attribute.

## Returns:
    None: This method does not return any value.

## Raises:
    None: This method does not explicitly raise any exceptions.

## State Changes:
    Attributes READ: self.argparser
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The self.argparser attribute must be initialized and accessible.
    Postconditions: The argument parser will include a new '-n'/'--dry-run' option.

## Side Effects:
    None: This method does not cause any I/O operations or external service calls.

### `csvkit.utilities.csvclean.CSVClean._format_error_row` · *method*

## Summary:
Formats a CSV validation error into a structured row for error reporting, including line number, error message, and the original row data.

## Description:
This private method transforms a CSVTestException object into a list format suitable for writing to an error output CSV file. It constructs a row that includes the line number and error message from the exception, followed by the complete original row data. This method is called during the error reporting phase of CSV cleaning operations to format error entries consistently.

The method is separated from the main error reporting logic to maintain clean separation of concerns, allowing the error formatting to be easily tested and modified independently while keeping the main CSV cleaning workflow focused on processing and validation.

## Args:
    error (CSVTestException): A validation error object containing line_number, msg, and row attributes

## Returns:
    list: A list containing [line_number, msg] followed by all fields from the original problematic row

## Raises:
    None explicitly raised - relies on CSVTestException attributes being properly populated

## State Changes:
    Attributes READ: error.line_number, error.msg, error.row
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The error parameter must be a CSVTestException instance with properly initialized attributes
    Postconditions: The returned list will always contain at least two elements (line_number and msg) plus any fields from the original row

## Side Effects:
    None - this is a pure transformation method with no I/O or external side effects

## `csvkit.utilities.csvclean.launch_new_instance` · *function*

## Summary:
Launches a new instance of the CSVClean utility to process CSV files, handling command-line argument parsing and execution flow.

## Description:
This function serves as the entry point for launching the CSVClean command-line utility. It creates an instance of the CSVClean class and invokes its run() method to execute the CSV cleaning workflow. The function is designed to be called by the command-line interface to initiate processing of CSV data according to the specified arguments.

The function extracts the instantiation and execution logic into a separate function to maintain clean separation between the utility's construction and execution phases. This approach allows for easier testing and potential reuse in different contexts while keeping the command-line interface simple and focused.

## Args:
    None: This function takes no parameters.

## Returns:
    None: This function does not return any value.

## Raises:
    Any exceptions that may be raised by CSVClean.__init__() or CSVClean.run() methods, including:
    - ValueError: If skip_lines argument is not an integer
    - RequiredHeaderError: If --no-header-row is used with -n/--names flag
    - NotImplementedError: If CSVClean's add_arguments or main methods are not properly overridden by the parent CSVKitUtility class

## Constraints:
    Preconditions:
        - The csvkit.utilities.csvclean module must be properly imported
        - The CSVClean class must be correctly defined and inherit from CSVKitUtility
        - Command-line arguments must be available in sys.argv or equivalent
        
    Postconditions:
        - A CSVClean instance is created and its run() method is invoked
        - All command-line arguments are processed through the CSVKitUtility framework
        - Input/output file handles are managed by the CSVKitUtility.run() method

## Side Effects:
    - Reads command-line arguments from sys.argv
    - May open and close input/output files during execution
    - Writes processing results to stdout/stderr
    - May modify global state through CSVKitUtility's argument parsing and file handling

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance] --> B[Create CSVClean instance]
    B --> C[Call utility.run()]
    C --> D{CSVKitUtility.run executes}
    D --> E[Argument parsing occurs]
    E --> F[Input file handling occurs]
    F --> G[Main processing logic executes]
    G --> H[Output written to stdout/stderr]
    H --> I[File handles closed]
    I --> J[Function completes]
```

## Examples:
```python
# Typical usage from command line
# python csvclean.py input.csv

# Or programmatically (though less common)
from csvkit.utilities.csvclean import launch_new_instance
launch_new_instance()
```

