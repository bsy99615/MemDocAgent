# `csvgrep.py`

## `csvkit.utilities.csvgrep.CSVGrep` · *class*

*No documentation generated.*

### `csvkit.utilities.csvgrep.CSVGrep.add_arguments` · *method*

## Summary:
Configures command-line argument parser with options for CSV grep filtering functionality.

## Description:
This method sets up the argument parser with various command-line options that control how CSV data is filtered using grep-like patterns. It defines parameters for selecting columns to search, specifying search patterns (literal string, regex, or file-based), controlling match behavior (invert, any/all columns), and displaying column information.

The method is part of the CSVGrep utility class and is called during the initialization phase to prepare the command-line interface before parsing user input. It enables users to filter CSV rows based on pattern matching within specified columns.

## Args:
    self: The CSVGrep instance whose argparser attribute is modified

## Returns:
    None: This method modifies the instance's argparser in-place and returns nothing

## Raises:
    None explicitly raised: This method only configures arguments and doesn't raise exceptions

## State Changes:
    Attributes READ: self.argparser (used to add arguments)
    Attributes WRITTEN: self.argparser (modified in-place with new arguments)

## Constraints:
    Preconditions: 
    - self.argparser must be initialized and accessible
    - This method should only be called during object initialization/setup phase
    
    Postconditions:
    - self.argparser contains all configured command-line arguments for CSV grep operations
    - All argument configurations are properly registered with the parser

## Side Effects:
    None: This method only modifies the internal argument parser configuration and doesn't perform I/O or external service calls

## Argument Details:
    -n, --names: Display column names and indices from the input CSV and exit
    -c, --columns: Specify comma-separated list of column indices, names or ranges to be searched (e.g., "1,id,3-5")
    -m, --match: Search for literal string pattern
    -r, --regex: Search using regular expression pattern
    -f, --file: Match against content of a file (one line per pattern, stripped of line separators)
    -i, --invert-match: Select non-matching rows instead of matching rows
    -a, --any-match: Select rows where any column matches instead of requiring all columns to match

### `csvkit.utilities.csvgrep.CSVGrep.main` · *method*

## Summary:
Filters CSV rows based on pattern matching criteria across specified columns and outputs matching rows to the designated output file.

## Description:
The main method implements the core filtering logic for the csvgrep utility, enabling users to extract CSV rows that match specified patterns in selected columns. It supports multiple matching modes including regex patterns, literal string matching, and file-based pattern matching. The method handles various operational modes including column name listing, interactive input waiting, and standard filtering operations.

This method is the primary execution entry point for the csvgrep utility and orchestrates the complete filtering workflow from argument validation through data processing and output generation.

## Args:
    self: The CSVGrep instance containing command-line arguments and processing state.

## Returns:
    None: This method performs I/O operations directly and does not return a value.

## Raises:
    SystemExit: Raised by self.argparser.error() when required arguments are missing or invalid
    IOError: Raised by underlying CSV processing when input/output files cannot be accessed

## State Changes:
    Attributes READ: 
        - self.args.names_only: Flag to display column names instead of filtering
        - self.args.columns: Column identifiers to search in
        - self.args.regex: Regular expression pattern for matching
        - self.args.pattern: Literal string pattern for matching
        - self.args.matchfile: File containing patterns for matching
        - self.args.inverse: Flag to invert matching logic
        - self.args.any_match: Flag to match any pattern instead of all patterns
        - self.reader_kwargs: Configuration for CSV reader creation
        - self.writer_kwargs: Configuration for CSV writer creation
        - self.output_file: Destination for output data
    Attributes WRITTEN: 
        - None: This method does not modify instance state beyond normal processing

## Constraints:
    Preconditions:
        - self.args must contain all required attributes from argument parsing
        - Input file must be accessible or stdin must be available for reading
        - At least one column must be specified for searching
        - One of regex, pattern, or matchfile must be specified for filtering criteria
        
    Postconditions:
        - If names_only is True, column names are written to output and method exits
        - If no input is provided, user is prompted to provide stdin input
        - Filtered CSV data is written to self.output_file with proper header row

## Side Effects:
    - Writes formatted column names or filtered CSV rows to self.output_file
    - Reads CSV data from self.input_file or stdin
    - Writes informational message to sys.stderr when waiting for stdin input
    - Opens and closes self.args.matchfile when using file-based pattern matching
    - Uses agate.csv.reader and agate.csv.writer for CSV processing
    - Creates FilteringCSVReader instance for pattern matching operations

## `csvkit.utilities.csvgrep.launch_new_instance` · *function*

## Summary:
Creates and executes a new instance of the CSVGrep utility for searching CSV files.

## Description:
The `launch_new_instance` function serves as a factory method that instantiates a CSVGrep utility and executes it. This function is typically invoked by command-line entry points to initialize and run the CSV grep functionality. It encapsulates the instantiation and execution workflow, providing a clean interface for launching the CSV grep utility.

This logic is extracted into its own function rather than being inlined because it separates the concern of utility instantiation from the command-line interface setup, making the code more modular and testable. It also allows for easier reuse of the instantiation and execution pattern in different contexts.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised by this function, though the underlying CSVGrep.run() method may raise exceptions from the CSVKitUtility base class or related CSV processing components.

## Constraints:
    Preconditions:
    - The function assumes that the command-line environment is properly set up with appropriate arguments
    - The CSVGrep class must be properly imported and available in the namespace
    
    Postconditions:
    - A CSVGrep utility instance is created and executed
    - The utility processes input according to command-line arguments
    - Standard output contains the filtered CSV results or column information

## Side Effects:
    - Reads from standard input or specified input files
    - Writes to standard output (or specified output file)
    - May read from additional files specified via the -f flag
    - May write to stderr when prompting for standard input

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance called] --> B[Create CSVGrep instance]
    B --> C[Call utility.run()]
    C --> D{utility.run() executes}
    D -->|Success| E[Output processed CSV to stdout]
    D -->|Exception| F[Exception propagated to caller]
```

## Examples:
```python
# Typical usage from command line:
# csvgrep -c 1 -m "search_term" input.csv

# Programmatic usage:
from csvkit.utilities.csvgrep import launch_new_instance
launch_new_instance()
```

