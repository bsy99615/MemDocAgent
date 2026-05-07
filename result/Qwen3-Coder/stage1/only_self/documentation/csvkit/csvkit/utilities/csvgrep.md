# `csvgrep.py`

## `csvkit.utilities.csvgrep.CSVGrep` · *class*

*No documentation generated.*

### `csvkit.utilities.csvgrep.CSVGrep.add_arguments` · *method*

## Summary:
Configures command-line argument parser with options for CSV grep functionality.

## Description:
This method extends the base CSVKitUtility argument parser with command-line options that control CSV filtering behavior. It is called during the initialization phase of CSVGrep utility to set up all available command-line arguments before parsing user input.

The method adds arguments for:
- Displaying column names and indices (--names/-n)
- Specifying columns to search (--columns/-c) 
- Defining search patterns (--match/-m, --regex/-r)
- File-based matching (--file/-f)
- Inverting match logic (--invert-match/-i)
- Selecting any vs all column matching (--any-match/-a)

This approach allows for flexible CSV row filtering similar to Unix grep but adapted for structured CSV data.

## Args:
    None - This is a method of a class that modifies its own argparser instance

## Returns:
    None - This method modifies the instance's argparser in-place

## Raises:
    None - This method doesn't raise exceptions directly, though argument parsing may raise errors

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies the argument parser instance)

## Constraints:
    Preconditions: 
    - self.argparser must be initialized and available (inherited from CSVKitUtility)
    - This method should only be called during object initialization, typically by CSVKitUtility.run()
    
    Postconditions:
    - The argparser instance contains all defined command-line arguments for CSV grep functionality
    - All argument definitions are properly registered with the parser

## Side Effects:
    - Modifies the self.argparser instance by adding new arguments to it
    - No external I/O operations or service calls

### `csvkit.utilities.csvgrep.CSVGrep.main` · *method*

## Summary:
Filters CSV rows based on pattern matching criteria across specified columns and outputs matching rows to stdout.

## Description:
This method implements the core filtering logic for the csvgrep utility, enabling users to search CSV data for rows containing specific patterns in designated columns. It supports regular expressions, literal pattern matching, and file-based pattern matching with flexible matching strategies (any match or all match) and inverse filtering options.

The method orchestrates the entire filtering workflow by:
1. Handling special cases like column name listing when -n/--names-only is specified
2. Validating input requirements and raising SystemExit for missing arguments
3. Setting up appropriate CSV readers and writers with proper configuration
4. Processing patterns into callable functions based on the matching mode
5. Applying filtering logic through FilteringCSVReader
6. Outputting filtered results with proper headers

## Args:
    self: The CSVGrep instance containing parsed arguments and configuration

## Returns:
    None: This method performs I/O operations and does not return a value, though it may exit early in certain cases

## Raises:
    SystemExit: Raised by self.argparser.error() when validation fails:
    - When no columns are specified using the -c option
    - When no pattern specification is provided (-r, -m, or -f options)
    - When input is expected but not provided (no file and no piped data)

## State Changes:
    Attributes READ: 
    - self.args: Command-line arguments parsed by argparse
    - self.reader_kwargs: Configuration for CSV reader creation
    - self.writer_kwargs: Configuration for CSV writer creation
    - self.output_file: Output file handle for writing results
    
    Attributes WRITTEN:
    - None: This method doesn't modify instance state directly

## Constraints:
    Preconditions:
    - At least one column must be specified using the -c option
    - One of -r (regex), -m (pattern), or -f (matchfile) must be specified unless -n (names-only) is used
    - Input data must be available (either from file or stdin)
    
    Postconditions:
    - If names_only is True, column names are printed and method exits early
    - If no matching rows are found, only the header row is written to output
    - All input data is processed and filtered according to specified criteria

## Side Effects:
    - Writes to stderr when waiting for standard input (when no input file is provided)
    - Writes filtered CSV data to the configured output file (stdout by default)
    - Reads from stdin when no input file is provided and additional input is expected
    - Closes the matchfile handle when using -f option

## `csvkit.utilities.csvgrep.launch_new_instance` · *function*

## Summary:
Creates and executes a new instance of the CSVGrep utility for searching CSV data.

## Description:
This function serves as the entry point for launching the CSVGrep command-line utility. It instantiates a CSVGrep object and invokes its run() method to process command-line arguments and execute the CSV search functionality. The function encapsulates the instantiation and execution workflow, providing a clean interface for starting the CSV grep utility.

This logic is extracted into its own function rather than being inlined in the main module to enable:
- Testability of the utility creation and execution flow
- Consistent instantiation pattern across different invocation contexts
- Separation of concerns between utility creation and execution
- Support for alternative launch mechanisms (like in unit tests or other entry points)

## Args:
    None

## Returns:
    None

## Raises:
    SystemExit: When the utility encounters invalid arguments or other fatal errors during execution
    Exception: Various exceptions may be raised during CSV processing or file I/O operations

## Constraints:
    Preconditions:
    - Command-line arguments must be available via sys.argv
    - Standard input/output streams must be accessible
    - Required CSV processing dependencies must be available
    - Input files (if specified) must be readable
    - Output destinations (if specified) must be writable
    
    Postconditions:
    - The CSV grep utility will either successfully process the input or terminate with an appropriate error message
    - All temporary resources will be cleaned up appropriately
    - Standard input/output streams will be left in a consistent state

## Side Effects:
    - Reads from standard input or specified input files (via CSVKitUtility's input_file handling)
    - Writes to standard output or specified output files (via CSVKitUtility's output_file handling)
    - May read from files specified via command-line arguments (when using -f flag)
    - Processes command-line arguments from sys.argv
    - May display usage information or error messages to stderr
    - May modify global state through CSVKitUtility's argument parsing and setup

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[Create CSVGrep instance]
    B --> C[Call utility.run()]
    C --> D{Input file handling}
    D -->|File specified| E[Open input file]
    D -->|No file| F[Use stdin]
    E --> G[Parse command-line arguments]
    F --> G
    G --> H{Validation checks}
    H -->|Invalid args| I[Display error and exit]
    H -->|Valid args| J[Process CSV data]
    J --> K[Apply filtering based on search criteria]
    K --> L[Write filtered results to output]
    L --> M[Cleanup and exit]
```

## Examples:
```python
# Typical usage in command line context
# python -m csvkit.utilities.csvgrep -c 1 -m "search_term" input.csv

# In test scenarios
from csvkit.utilities.csvgrep import launch_new_instance
launch_new_instance()  # Creates and runs CSVGrep instance
```

