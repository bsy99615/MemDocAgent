# `csvsort.py`

## `csvkit.utilities.csvsort.CSVSort` · *class*

## Summary
A command-line utility for sorting CSV files, similar to the Unix "sort" command but designed for tabular data.

## Description
The CSVSort class implements a command-line utility that sorts CSV files based on specified columns. It inherits from CSVKitUtility, providing standard CSV processing capabilities like argument parsing, file handling, and CSV dialect detection. Users can sort by one or more columns, specify sort order (ascending/descending), limit CSV sniffing, and control type inference.

This class serves as a specialized tool for tabular data manipulation, enabling efficient sorting operations on CSV datasets through a familiar command-line interface pattern.

## State
- `description` (str): Class-level attribute describing the utility's purpose. Value: 'Sort CSV files. Like the Unix "sort" command, but for tabular data.'
- `argparser`: Instance attribute created by the parent class, used for command-line argument parsing
- `args`: Instance attribute containing parsed command-line arguments
- `input_file`: Instance attribute referencing the opened input file handle
- `output_file`: Instance attribute referencing the output file handle (defaults to stdout)
- `reader_kwargs`: Instance attribute containing keyword arguments for CSV reader configuration
- `writer_kwargs`: Instance attribute containing keyword arguments for CSV writer configuration

## Lifecycle
**Creation**: Instances are created automatically by the CSVKit framework when invoked from the command line. The constructor inherits from CSVKitUtility and sets up argument parsing.

**Usage**: The utility follows the standard CSVKit pattern:
1. Command-line arguments are parsed via `add_arguments()` and `argparser.parse_args()`
2. The `run()` method in the parent class orchestrates execution:
   - Opens input file if needed
   - Calls `main()` method
   - Handles cleanup of input file
3. In `main()`, the sorting process occurs:
   - If `--names` flag is set, column names are displayed and execution ends
   - Input validation ensures data is provided
   - CSV data is loaded into an agate Table
   - Column identifiers are parsed into zero-based indices
   - Table is sorted by specified columns
   - Sorted results are written to output

**Destruction**: Cleanup is handled automatically by the parent class's `run()` method, which closes the input file when finished.

## Method Map
```mermaid
flowchart TD
    A[CSVSort.run()] --> B[CSVSort.__init__()]
    B --> C[CSVKitUtility.__init__()]
    C --> D[CSVKitUtility._init_common_parser()]
    D --> E[CSVSort.add_arguments()]
    E --> F[CSVKitUtility.argparser.parse_args()]
    F --> G[CSVSort.main()]
    G --> H[CSVSort.print_column_names()]
    G --> I[CSVSort.additional_input_expected()]
    I --> J{Input expected?}
    J -->|No| K[Error: Provide input]
    J -->|Yes| L[agate.Table.from_csv()]
    L --> M[parse_column_identifiers()]
    M --> N[agate.Table.order_by()]
    N --> O[agate.Table.to_csv()]
```

## Raises
- `argparse.ArgumentTypeError`: Raised by argument parser when invalid argument values are provided
- `RequiredHeaderError`: Raised when `--no-header-row` is used with `--names` flag
- `ValueError`: Raised by `skip_lines()` when skip_lines argument is not an integer
- `UnicodeDecodeError`: Potentially raised during file reading if encoding issues occur (handled by parent class)

## Example
```python
# Sort a CSV file by the 'name' column in ascending order
# Command line usage:
# python csvsort.py -c name data.csv

# Or programmatically:
from csvkit.utilities.csvsort import CSVSort

# Create instance with arguments
utility = CSVSort(['-c', 'name', 'input.csv'])

# Run the sorting operation
utility.run()
```

The utility can also be used to display column names:
```bash
# Display column names and indices
python csvsort.py -n data.csv
```

Or sort in descending order:
```bash
# Sort by 'age' column in descending order
python csvsort.py -c age -r data.csv
```

### `csvkit.utilities.csvsort.CSVSort.add_arguments` · *method*

## Summary:
Configures command-line arguments for the CSV sorting utility, defining options for sorting behavior, column selection, and CSV parsing parameters.

## Description:
This method initializes and registers all available command-line arguments with the argument parser instance (`self.argparser`) used by the CSVSort utility. It sets up options for specifying sort columns, controlling sort direction, managing CSV parsing behavior, and displaying column information. The method is automatically invoked during the initialization phase of CSVKitUtility subclasses.

## Args:
    self: The CSVSort instance whose argparser will be configured with command-line options.

## Returns:
    None: This method modifies the instance's argparser in-place and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions, though argument parsing may raise argparse-related exceptions during execution.

## State Changes:
    Attributes READ: 
        - self.argparser: Used to register command-line arguments
    Attributes WRITTEN:
        - self.argparser: Modified to include new command-line argument definitions

## Constraints:
    Preconditions:
        - The instance must have an initialized `argparser` attribute (inherited from CSVKitUtility)
        - The method should only be called during object initialization or setup phase
        
    Postconditions:
        - The `self.argparser` instance contains all registered command-line arguments
        - All argument definitions are properly configured with help text, types, and default values

## Side Effects:
    None: This method only modifies the internal argument parser configuration and does not perform I/O operations or mutate external state.

### `csvkit.utilities.csvsort.CSVSort.main` · *method*

## Summary:
Sorts CSV data by specified columns and writes the result to output.

## Description:
This method implements the core sorting functionality for the csvsort utility. It processes CSV input according to command-line arguments, sorts the data by specified columns, and outputs the sorted results. The method handles various configuration options including column selection, sorting direction, and CSV parsing parameters.

## Args:
    self: The CSVSort instance containing command-line arguments and file handles.

## Returns:
    None: This method performs I/O operations and does not return a value.

## Raises:
    SystemExit: Raised by argparser.error() when no input file is provided and no piped data is available.

## State Changes:
    Attributes READ:
        - self.args.names_only: Flag to control column name printing
        - self.args.columns: Column identifiers for sorting
        - self.args.reverse: Flag to control sorting order
        - self.args.sniff_limit: Limit for CSV dialect detection
        - self.args.skip_lines: Number of initial lines to skip
        - self.args.input_path: Path to input file
        - self.args.encoding: Character encoding for input file
        - self.args.delimiter: Delimiter character for CSV parsing
        - self.args.tabs: Flag indicating tab-delimited input
        - self.args.quotechar: Quote character for CSV parsing
        - self.args.quoting: Quoting style for CSV parsing
        - self.args.doublequote: Flag for double quote handling
        - self.args.escapechar: Escape character for CSV parsing
        - self.args.field_size_limit: Maximum field size limit
        - self.args.skipinitialspace: Flag to ignore whitespace after delimiter
        - self.args.no_header_row: Flag indicating no header row in input
        - self.args.zero_based: Flag for zero-based column indexing
        - self.args.no_inference: Flag to disable type inference
        - self.args.date_format: Date format string for parsing dates
        - self.args.datetime_format: Datetime format string for parsing datetimes
        - self.args.blanks: Flag to treat blank values as null
        - self.args.null_values: Additional null value specifications
        - self.args.locale: Locale for number formatting
        
    Attributes WRITTEN:
        - self.input_file: Input file handle (opened via _open_input_file)
        - self.output_file: Output file handle (stdout or specified file)
        - self.reader_kwargs: Dictionary of CSV reader keyword arguments
        - self.writer_kwargs: Dictionary of CSV writer keyword arguments

## Constraints:
    Preconditions:
        - Command-line arguments must be parsed and available in self.args
        - Either an input file path must be provided or piped data must be available
        - Column identifiers in self.args.columns must be valid for the CSV schema
        - CSV file must be readable with the specified encoding and parameters
        
    Postconditions:
        - If names_only flag is set, column names are printed to output and method returns early
        - If input validation passes, a sorted CSV table is written to output_file
        - All temporary resources are properly managed through context managers

## Side Effects:
    - Reads from input file or stdin
    - Writes to output file or stdout
    - May raise SystemExit if input validation fails
    - Opens and closes file handles as needed
    - Processes CSV data through agate library

## `csvkit.utilities.csvsort.launch_new_instance` · *function*

## Summary
Creates and executes a new instance of the CSVSort command-line utility for sorting CSV files.

## Description
This function serves as the entry point for launching the CSVSort command-line utility. It instantiates a CSVSort object and invokes its run method to process command-line arguments and sort CSV data according to specified columns. The function follows the standard csvkit utility pattern where each command-line tool provides a launch_new_instance function that handles instantiation and execution.

The CSVSort utility enables users to sort CSV files by one or more columns in ascending or descending order, similar to the Unix "sort" command but designed specifically for tabular data. It supports various sorting options including column selection, sort direction, and CSV parsing parameters.

This function is typically called by the csvkit command-line framework when the 'csvsort' command is executed, providing a consistent interface for initializing and running the CSV sorting utility regardless of how it's invoked.

## Args
None

## Returns
None

## Raises
None explicitly raised by this function, though the underlying CSVSort.run() method may raise:
- SystemExit: When command-line argument validation fails or no input is provided
- argparse.ArgumentTypeError: When invalid argument values are provided
- RequiredHeaderError: When --no-header-row is used with --names flag
- ValueError: When skip_lines argument is not an integer
- UnicodeDecodeError: When encoding issues occur during file operations (handled by parent class)

## Constraints
Preconditions:
- The csvkit command-line framework must be properly initialized
- Command-line arguments must be available for parsing (typically via sys.argv)
- Input file paths (if specified) must be accessible
- Output file paths (if specified) must be writable

Postconditions:
- A CSVSort instance is created and executed
- Command-line arguments are parsed and processed
- CSV data is sorted according to specified criteria
- Appropriate output is generated to stdout/stderr based on operation mode

## Side Effects
- Reads from input file(s) or stdin when processing CSV data
- Writes to output file(s) or stdout when producing sorted results
- May read command-line arguments from sys.argv
- May raise system exceptions if file operations fail

## Control Flow
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[CSVSort()]
    B --> C[utility.run()]
    C --> D{CSVKitUtility.run()}
    D --> E[Parse command-line args]
    E --> F{Input file specified?}
    F -->|Yes| G[Open input file]
    F -->|No| H[Read from stdin]
    G --> I[CSVSort.main()]
    H --> I
    I --> J{Names only flag?}
    J -->|Yes| K[Print column names and exit]
    J -->|No| L[Load CSV data into agate Table]
    L --> M[Parse column identifiers]
    M --> N[Sort table by specified columns]
    N --> O[Write sorted results to output]
    O --> P[End execution]
```

## Examples
```bash
# Sort a CSV file by the 'name' column in ascending order
csvsort -c name data.csv

# Sort by 'age' column in descending order
csvsort -c age -r data.csv

# Sort by multiple columns
csvsort -c department,name data.csv

# Display column names and indices
csvsort -n data.csv
```

Programmatic usage:
```python
# Create and run CSVSort utility programmatically
from csvkit.utilities.csvsort import launch_new_instance
launch_new_instance()
```

