# `csvcut.py`

## `csvkit.utilities.csvcut.CSVCut` · *class*

## Summary:
CSVCut is a command-line utility that filters and truncates CSV files, similar to the Unix "cut" command but designed for tabular data with support for column names, ranges, and various filtering options.

## Description:
The CSVCut utility allows users to extract specific columns from CSV files, either by specifying column indices, names, or ranges, or by excluding certain columns. It supports advanced features like deleting empty rows after filtering and displaying column metadata. This utility is part of the csvkit toolkit and inherits standard CSV processing capabilities from CSVKitUtility.

The class is intended to be instantiated and run through the csvkit command-line interface, where it processes CSV data according to user-specified column selections and filtering criteria. When the -n/--names flag is used, it displays column names and exits without processing data. Otherwise, it processes the CSV data by selecting specified columns and optionally filtering out empty rows.

## State:
- description (str): Set to 'Filter and truncate CSV files. Like the Unix "cut" command, but for tabular data.'
- override_flags (list[str]): Set to ['L', 'blanks', 'date-format', 'datetime-format'] to exclude certain standard CSV flags from argument parsing
- args (argparse.Namespace): Parsed command-line arguments containing:
  - names_only (bool): True when -n/--names flag is used to display column names only
  - columns (str): Comma-separated list of column indices, names, or ranges to extract (e.g., "1,id,3-5")
  - not_columns (str): Comma-separated list of column indices, names, or ranges to exclude (e.g., "1,id,3-5")
  - delete_empty (bool): True when -x/--delete-empty-rows flag is used to remove empty rows
- reader_kwargs (dict): Configuration parameters for CSV readers inherited from CSVKitUtility
- writer_kwargs (dict): Configuration parameters for CSV writers inherited from CSVKitUtility

## Lifecycle:
- Creation: Instantiated via command-line interface or programmatically with arguments
- Usage: Called through CSVKitUtility.run() method which orchestrates argument parsing and execution
  1. Arguments are parsed via add_arguments()
  2. If names_only flag is set, column names are displayed and main() returns early
  3. If no input is provided, the utility waits for standard input
  4. CSV data is processed using inherited methods to extract rows and column information
  5. Selected columns are written to output with appropriate header row
  6. Rows are filtered based on delete_empty flag if specified
- Destruction: Automatically managed by CSVKitUtility parent class which handles file closing

## Method Map:
```mermaid
graph TD
    A[CSVCut.main] --> B{names_only?}
    B -->|Yes| C[CSVKitUtility.print_column_names]
    B -->|No| D[CSVKitUtility.additional_input_expected]
    D --> E{stdin connected?}
    E -->|Yes| F[sys.stderr write message]
    E -->|No| G[Continue processing]
    G --> H[CSVKitUtility.get_rows_and_column_names_and_column_ids]
    H --> I[agate.csv.writer]
    I --> J[Process rows and write selected columns]
    J --> K{delete_empty?}
    K -->|Yes| L[Check if row has any values]
    L --> M{any(out_row)?}
    M -->|Yes| N[Write row]
    M -->|No| O[Skip row]
    K -->|No| P[Write row]
    P --> Q[End]
    N --> Q
    O --> Q
```

## Raises:
- None explicitly raised by CSVCut constructor
- Exceptions may be raised by inherited methods when:
  - Invalid column specifications are provided (parsing errors)
  - Input files cannot be opened or read
  - Output files cannot be written to
  - Command-line arguments are invalid
  - CSV parsing fails due to malformed data

## Example:
```python
# Command line usage:
# csvcut -c 1,3,5 input.csv          # Extract columns 1, 3, and 5
# csvcut -c name,age input.csv       # Extract columns named 'name' and 'age'
# csvcut -C 2,4 input.csv            # Exclude columns 2 and 4
# csvcut -n input.csv                # Display column names only
# csvcut -x input.csv                # Remove empty rows after cutting
# csvcut -c 1-3 -x input.csv         # Extract first three columns and remove empty rows

# Programmatic usage:
from csvkit.utilities.csvcut import CSVCut
utility = CSVCut(['-c', '1,3', 'input.csv'])
utility.run()
```

### `csvkit.utilities.csvcut.CSVCut.add_arguments` · *method*

## Summary:
Configures command-line arguments for the CSV cut utility, defining options for column selection, display, and row filtering.

## Description:
This method sets up the argument parser with command-line options that control how CSV data is filtered and truncated. It is called during the initialization phase of the CSVCut utility to define available user-facing options. The method follows the standard CSVKit pattern of configuring CLI arguments in the add_arguments method of utility classes.

## Args:
    self: The CSVCut instance whose argparser will be configured

## Returns:
    None: This method modifies the instance's argparser in-place and returns nothing

## Raises:
    None: This method does not raise exceptions directly

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modified in-place to add arguments)

## Constraints:
    Preconditions: The method assumes self.argparser exists and is a proper ArgumentParser instance
    Postconditions: The argparser instance will contain the defined command-line arguments

## Side Effects:
    None: This method only modifies the internal argument parser configuration and has no external I/O or side effects

### `csvkit.utilities.csvcut.CSVCut.main` · *method*

## Summary:
Processes CSV data by filtering columns according to specified criteria and optionally deleting empty rows, or displays column names when requested.

## Description:
The main method implements the core functionality of the csvcut utility. When the --names/-n flag is specified, it displays column names with indices and exits. Otherwise, it reads CSV data, selects specified columns (using --columns or --not-columns flags), and writes the filtered results to output. The method handles input validation, displays user prompts for stdin input, and supports deletion of completely empty rows via the --delete-empty-rows flag.

This method serves as the central coordination point for the CSV cutting operation, orchestrating input handling, column selection, and output generation while managing special cases like empty row deletion and interactive input mode. It leverages parent class methods for robust CSV processing and follows the standard csvkit utility pattern.

## Args:
    self: The CSVCut instance containing command-line arguments and processing state

## Returns:
    None: This method performs I/O operations directly and does not return a value

## Raises:
    None: Exceptions from underlying operations are handled by the parent class

## State Changes:
    Attributes READ: 
        - self.args.names_only: Boolean flag to determine if only column names should be displayed
        - self.args.delete_empty: Boolean flag to determine if empty rows should be deleted
        - self.args.columns: String specifying columns to include (comma-separated indices, names, or ranges)
        - self.args.not_columns: String specifying columns to exclude (comma-separated indices, names, or ranges)
        - self.reader_kwargs: CSV reader configuration parameters
        - self.writer_kwargs: CSV writer configuration parameters
        - self.output_file: Output destination for processed CSV data
    
    Attributes WRITTEN: 
        - None: This method doesn't modify instance state beyond I/O operations

## Constraints:
    Preconditions:
        - self.args must contain all required attributes (names_only, delete_empty, columns, not_columns, etc.)
        - self.input_file must be properly initialized and readable
        - self.output_file must be writable
        - CSV data must be accessible through self.input_file
    
    Postconditions:
        - If names_only is True, column names are written to self.output_file and method returns early
        - If names_only is False, filtered CSV data is written to self.output_file with selected columns
        - All CSV processing parameters are properly applied according to command-line flags

## Side Effects:
    - Writes to self.output_file (typically stdout) with processed CSV data or column names
    - Writes to sys.stderr (standard error) when waiting for stdin input
    - Reads from self.input_file (CSV file or stdin)
    - Uses agate.csv.writer for output formatting
    - Calls parent class methods for input handling and data processing

## `csvkit.utilities.csvcut.launch_new_instance` · *function*

## Summary:
Creates and executes a new instance of the CSVCut command-line utility for filtering and truncating CSV files.

## Description:
This function serves as the primary entry point for launching the csvcut command-line utility. It instantiates a CSVCut class and invokes its run method to process CSV data according to command-line arguments.

The csvcut utility allows users to extract specific columns from CSV files, either by specifying column indices, names, or ranges, or by excluding certain columns. It supports advanced features like deleting empty rows after filtering and displaying column metadata.

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
    - The function executes the complete CSV column filtering workflow
    - Either processes input CSV files and generates output, or displays diagnostic information
    - Function does not return any meaningful value

## Side Effects:
    - Parses command-line arguments from sys.argv
    - Reads input CSV files from disk or stdin
    - Writes processed CSV data to stdout or specified output file
    - May display column names to stdout when -n/--names flag is used
    - Writes error information to stderr when processing issues occur

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance called] --> B[Create CSVCut instance]
    B --> C[Call utility.run()]
    C --> D{Argument parsing complete}
    D --> E{names_only flag set?}
    E -->|Yes| F[Print column names and exit]
    E -->|No| G{Additional input expected?}
    G -->|Yes| H{stdin connected?}
    H -->|Yes| I[Write waiting message to stderr]
    H -->|No| J[Continue processing]
    G -->|No| K[Continue processing]
    J --> L[Open input file or stdin]
    L --> M[Get rows and column information]
    M --> N[Process rows and select columns]
    N --> O{delete_empty flag set?}
    O -->|Yes| P[Filter out empty rows]
    P --> Q[Write results to output]
    O -->|No| Q
    Q --> R[End]
```

## Examples:
```python
# Launches csvcut utility with default settings
# This is typically called internally by the csvcut command
launch_new_instance()

# Typical command-line usage (which internally calls this function):
# csvcut -c 1,3 input.csv

# Extract columns by name:
# csvcut -c id,name,age input.csv

# Exclude specific columns:
# csvcut -C 2,4 input.csv

# Display column names only:
# csvcut -n input.csv

# Delete empty rows after filtering:
# csvcut -c 1,3 -x input.csv
```

