# `csvsort.py`

## `csvkit.utilities.csvsort.CSVSort` · *class*

## Summary:
A command-line utility for sorting CSV files, implementing the Unix "sort" command functionality for tabular data.

## Description:
CSVSort provides functionality to sort CSV files based on specified columns, similar to the Unix sort command but adapted for tabular data. It accepts various command-line arguments to control sorting behavior including column selection, sort order, and CSV parsing options. The utility can display column names, sort by specific columns, or sort all columns, with support for ascending or descending order.

This class is part of the csvkit suite of command-line tools and inherits from CSVKitUtility, leveraging its common CSV processing capabilities such as file handling, argument parsing, and CSV reader/writer configuration. It is designed to be instantiated and run through the standard CSVKit utility execution flow.

## State:
- `description` (str): Class variable describing the utility's purpose
- `argparser`: argparse.ArgumentParser instance inherited from CSVKitUtility for command-line argument parsing
- `args`: Parsed command-line arguments from argparse
- `input_file`: File-like object for reading input (inherited from CSVKitUtility)
- `output_file`: File-like object for writing output (inherited from CSVKitUtility)
- `reader_kwargs`: Dictionary of keyword arguments for CSV reader construction (inherited from CSVKitUtility)
- `writer_kwargs`: Dictionary of keyword arguments for CSV writer construction (inherited from CSVKitUtility)

## Lifecycle:
Creation: Instantiate with optional args list and output_file parameter. The constructor:
1. Initializes the common argument parser through CSVKitUtility parent class
2. Calls add_arguments() to configure command-line options
3. Parses arguments using argparse
4. Sets up output file handle
5. Extracts CSV reader and writer kwargs
6. Installs exception handler
7. Sets up SIGPIPE signal handling

Usage: Call `run()` method which orchestrates the execution flow:
1. If `-n`/`--names` flag is set, prints column names and exits
2. Validates that input is provided (file or piped data) using `additional_input_expected()`
3. Reads input CSV using `agate.Table.from_csv()` with configured parameters including sniff limit, column types, and reader kwargs
4. Parses column identifiers using `parse_column_identifiers()` with column names and offset
5. Sorts the table using `table.order_by()` with specified columns and reverse flag
6. Writes sorted results to output using `table.to_csv()` with writer kwargs

Destruction: Automatic cleanup occurs through context managers and file closing in the run() method inherited from CSVKitUtility.

## Method Map:
```mermaid
graph TD
    A[run()] --> B{args.names_only?}
    B -- Yes --> C[print_column_names()]
    B -- No --> D[additional_input_expected()]
    D -- Yes --> E[argparser.error()]
    D -- No --> F[agate.Table.from_csv()]
    F --> G[parse_column_identifiers()]
    G --> H[table.order_by()]
    H --> I[table.to_csv()]
```

## Raises:
- argparse.ArgumentTypeError: Raised by argument parser when invalid argument values are provided
- RequiredHeaderError: Raised by print_column_names() when --no-header-row is used with -n/--names
- ValueError: Raised by skip_lines() when skip_lines argument is not an integer
- UnicodeDecodeError: Handled by custom exception handler for encoding issues
- SystemExit: Raised by argparser.error() when required input is missing

## Example:
```python
# Basic usage to sort all columns in ascending order
from csvkit.utilities.csvsort import CSVSort

# Sort entire file by all columns in ascending order
sort_tool = CSVSort(['input.csv', '-o', 'output.csv'])
sort_tool.run()

# Sort by specific columns in descending order
sort_tool = CSVSort(['input.csv', '-c', 'name,age', '-r', '-o', 'output.csv'])
sort_tool.run()

# Display column names only
sort_tool = CSVSort(['input.csv', '-n'])
sort_tool.run()

# Sort with limited sniffing
sort_tool = CSVSort(['input.csv', '-y', '2048', '-o', 'output.csv'])
sort_tool.run()
```

### `csvkit.utilities.csvsort.CSVSort.add_arguments` · *method*

## Summary:
Configures command-line arguments for the CSV sorting utility, enabling users to specify sorting columns, sort direction, and CSV parsing options.

## Description:
This method extends the base argument parser with specialized options for sorting CSV data. It adds flags and parameters that control how CSV data is sorted, including which columns to sort by, whether to reverse the sort order, and various CSV parsing behaviors. The method is called during the initialization phase of CSVKit utilities to set up the command-line interface.

This logic is encapsulated in its own method because:
1. It follows the CSVKitUtility pattern where each subclass implements add_arguments() to define its specific CLI interface
2. It separates argument definition from business logic, making the code more modular and testable
3. It allows for consistent argument handling across all CSVKit utilities while enabling utility-specific customization

## Args:
    self: The CSVSort instance whose argparser will be modified

## Returns:
    None: This method modifies the instance's argparser in-place and returns nothing

## Raises:
    None: This method does not raise exceptions directly, though argument parsing may raise argparse errors

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modified in-place)

## Constraints:
    Preconditions:
        - The instance must have an initialized argparser attribute (inherited from CSVKitUtility)
        - The method should only be called during object initialization/setup phase
        
    Postconditions:
        - The argparser contains all the defined arguments for CSV sorting
        - All argument definitions are properly registered with the parser

## Side Effects:
    None: This method only modifies the internal argparser object and doesn't perform I/O or external service calls

## Arguments Added:
    - `-n, --names`: Display column names and indices from the input CSV and exit
    - `-c, --columns`: A comma-separated list of column indices, names or ranges to sort by (e.g., "1,id,3-5"). Defaults to all columns
    - `-r, --reverse`: Sort in descending order
    - `-y, --snifflimit`: Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely, or "-1" to sniff the entire file
    - `-I, --no-inference`: Disable type inference when parsing the input

### `csvkit.utilities.csvsort.CSVSort.main` · *method*

## Summary:
Sorts CSV data by specified columns and writes the result to output, or displays column names when requested.

## Description:
The main method implements the core functionality of the csvsort utility, which sorts CSV data according to specified column criteria. It handles two primary modes: displaying column names (--names flag) or performing actual sorting. The method processes input CSV data through agate's Table API, applies column-based sorting, and outputs the sorted results.

This method is the entry point for the CSV sorting functionality and orchestrates the complete workflow from input parsing to output generation. It supports sorting by multiple columns, reverse ordering, and various CSV parsing options.

## Args:
    self: The CSVSort instance containing parsed arguments and file handles

## Returns:
    None: This method performs I/O operations and does not return a value

## Raises:
    SystemExit: Raised by argparser.error() when no input file or piped data is provided
    ColumnIdentifierError: Raised by parse_column_identifiers() when column identifiers cannot be resolved
    UnicodeDecodeError: Raised by agate.Table.from_csv() when input file has encoding issues
    IOError: Raised by file I/O operations when reading input or writing output fails

## State Changes:
    Attributes READ:
        - self.args: Parsed command-line arguments from argparse
        - self.input_file: File handle for reading input CSV data
        - self.output_file: File handle for writing output CSV data
        - self.reader_kwargs: Keyword arguments for CSV reader configuration
        - self.writer_kwargs: Keyword arguments for CSV writer configuration
        - self.args.names_only: Boolean flag indicating whether to display column names only
        - self.args.columns: String specifying column identifiers for sorting
        - self.args.reverse: Boolean flag indicating reverse sorting order
        - self.args.sniff_limit: Integer limit for CSV dialect sniffing
        - self.args.skip_lines: Integer number of lines to skip at beginning of file
        - self.args.no_inference: Boolean flag to disable type inference

    Attributes WRITTEN:
        - None: This method does not modify instance attributes directly

## Constraints:
    Preconditions:
        - When names_only is False, input file must be provided via command line argument or piped data
        - Column identifiers in self.args.columns must be resolvable to valid column indices
        - Valid column names must exist in the input CSV header row
        - If sniff_limit is specified, it must be >= -1

    Postconditions:
        - When names_only is True, column names are printed to stdout and method exits
        - When names_only is False, sorted CSV data is written to output_file
        - The sorted table maintains the same column structure as the input

## Side Effects:
    - Reads from self.input_file (file or stdin)
    - Writes to self.output_file (file or stdout)
    - May read from stdin when no input file is provided
    - May raise SystemExit when validation fails
    - Uses agate library for CSV parsing and sorting operations

## Usage Examples:
    # Sort by first column in ascending order
    csvsort input.csv
    
    # Sort by first column in descending order  
    csvsort -r input.csv
    
    # Sort by specific columns
    csvsort -c "name,age" input.csv
    
    # Display column names only
    csvsort -n input.csv

## `csvkit.utilities.csvsort.launch_new_instance` · *function*

## Summary:
Creates and executes a new CSVSort utility instance to sort CSV files based on specified columns.

## Description:
This function serves as the entry point for launching the CSVSort command-line utility. It instantiates a CSVSort object and invokes its run() method to process command-line arguments and execute the CSV sorting functionality. The function follows the standard csvkit pattern where command-line utilities are instantiated and executed through a dedicated launch function.

This logic is extracted into its own function rather than being inlined in the main module to enable:
- Consistent instantiation pattern across different invocation contexts
- Testability of the utility creation and execution flow
- Separation of concerns between utility creation and execution
- Support for alternative launch mechanisms (like in unit tests or other entry points)

## Args:
    None

## Returns:
    None

## Raises:
    SystemExit: Raised by CSVSort.run() when argument validation fails or when the utility encounters fatal errors during execution
    Various exceptions from file I/O operations handled by CSVKitUtility parent class
    argparse.ArgumentTypeError: Raised by argument parser when invalid argument values are provided
    UnicodeDecodeError: Potentially raised during CSV reading if encoding issues occur (handled by parent class)
    RequiredHeaderError: Raised by print_column_names() when --no-header-row is used with -n/--names

## Constraints:
    Preconditions:
    - Command-line arguments must be available via sys.argv for parsing
    - Standard input/output streams must be accessible
    - Required CSV processing dependencies must be available
    - Input files (if specified) must be readable
    
    Postconditions:
    - A CSVSort utility instance is created and executed
    - CSV data is sorted according to specified columns and sort order
    - Sorted output is written to stdout or specified output file
    - All temporary resources are properly cleaned up

## Side Effects:
    - Reads from standard input or specified input files (via CSVKitUtility's input_file handling)
    - Writes sorted CSV output to standard output or specified output file (via CSVKitUtility's output_file handling)
    - Processes command-line arguments from sys.argv through CSVKitUtility's argument parser
    - May display usage information or error messages to stderr

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[Create CSVSort instance]
    B --> C[Call CSVSort.run()]
    C --> D{Input file handling}
    D -->|File specified| E[Open input file]
    D -->|No file| F[Use stdin]
    E --> G[Parse command-line arguments]
    F --> G
    G --> H{Validation checks}
    H -->|Invalid args| I[Display error and exit]
    H -->|Valid args| J[Process CSV data]
    J --> K[Read CSV into agate.Table]
    K --> L[Parse column identifiers]
    L --> M[Sort table using table.order_by()]
    M --> N[Write sorted results to output]
    N --> O[Cleanup and exit]
```

## Examples:
```bash
# Sort entire file by all columns in ascending order
csvsort input.csv > sorted_output.csv

# Sort by specific columns in descending order
csvsort -c name,age -r input.csv > sorted_output.csv

# Display column names only
csvsort -n input.csv

# Sort with limited sniffing
csvsort -y 2048 input.csv > sorted_output.csv
```

