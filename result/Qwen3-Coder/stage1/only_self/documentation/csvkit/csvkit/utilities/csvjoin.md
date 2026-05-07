# `csvjoin.py`

## `csvkit.utilities.csvjoin.CSVJoin` · *class*

## Summary:
A command-line utility that executes SQL-like JOIN operations to merge multiple CSV files based on specified column(s).

## Description:
The CSVJoin class implements a command-line tool for performing JOIN operations on multiple CSV files, similar to SQL JOINs. It allows users to merge CSV datasets based on common column values, supporting various JOIN types including inner, left, right, and full outer joins. The class inherits from CSVKitUtility and provides a standardized interface for CSV processing with argument parsing, file handling, and CSV reading capabilities.

This utility is particularly useful for combining related datasets from multiple sources into a single coherent view. It reads all input files into memory to perform the join operations, so it should not be used with very large files due to memory constraints.

## State:
- `argparser`: Argument parser instance inherited from CSVKitUtility
- `args`: Parsed command-line arguments
- `output_file`: Output file handle for writing results (inherited from CSVKitUtility)
- `reader_kwargs`: Keyword arguments for CSV reader construction (inherited from CSVKitUtility)
- `writer_kwargs`: Keyword arguments for CSV writer construction (inherited from CSVKitUtility)

## Lifecycle:
Creation: Instantiate CSVJoin with command-line arguments. The constructor automatically initializes the argument parser and parses arguments through the parent class's run() method.

Usage: Call the `run()` method which:
1. Validates input arguments via argument parser error handling
2. Opens all specified input files using `_open_input_file()`
3. Reads CSV data from all files into memory using `agate.Table.from_csv()`
4. Performs the specified JOIN operation on the tables using `agate.Table.join()`
5. Writes the resulting merged table to output using `jointab.to_csv()`

Destruction: Automatic cleanup occurs through the parent class's run() method which closes input files and manages resource cleanup.

## Method Map:
```mermaid
graph TD
    A[run()] --> B[add_arguments()]
    A --> C[main()]
    C --> D[isatty(sys.stdin) and input_paths == ['-']]
    C --> E[_open_input_file()]
    C --> F[_parse_join_column_names()]
    C --> G[get_column_types()]
    C --> H[agate.Table.from_csv()]
    C --> I[match_column_identifier()]
    C --> J[agate.Table.join()]
    C --> K[jointab.to_csv()]
```

## Raises:
- SystemExit: Raised by argparser.error() when validation fails (invalid arguments, missing required parameters)
- UnicodeDecodeError: Propagated from file reading operations when encoding issues occur
- ColumnIdentifierError: Raised by match_column_identifier() when column names/indices are invalid
- ValueError: May be raised by argument parsing when invalid values are provided for numeric arguments

## Example:
```python
# Join two CSV files on a common column
csvjoin -c id file1.csv file2.csv > merged_output.csv

# Perform a left outer join on multiple files
csvjoin --left -c "id,name" file1.csv file2.csv file3.csv > left_joined.csv

# Perform a full outer join with custom snifflimit
csvjoin --outer -y 2048 file1.csv file2.csv > full_joined.csv

# Join files without specifying columns (sequential join)
csvjoin file1.csv file2.csv > sequential_joined.csv

# Join with column indices instead of names
csvjoin -c 1 file1.csv file2.csv > indexed_joined.csv
```

### `csvkit.utilities.csvjoin.CSVJoin.add_arguments` · *method*

## Summary:
Configures command-line argument parser with options for joining CSV files.

## Description:
This method sets up the argument parser with all available command-line options for the CSV join utility. It defines how users can specify input files, join columns, join types, and various CSV parsing options. The method is part of the CSVKit CLI utility framework and is called during the initialization phase of the CSVJoin utility.

## Args:
    self: The CSVJoin instance whose argparser will be configured

## Returns:
    None: This method modifies the instance's argparser in-place and returns nothing

## Raises:
    None: This method does not raise exceptions directly

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies the argument parser configuration)

## Constraints:
    Preconditions: The method assumes self.argparser exists and is a proper ArgumentParser instance
    Postconditions: The argparser will contain all defined command-line arguments for CSV joining operations

## Side Effects:
    None: This method only configures the argument parser and doesn't perform I/O or external service calls

### `csvkit.utilities.csvjoin.CSVJoin.main` · *method*

## Summary:
Performs CSV file joining operations with support for inner, left, right, and outer joins across multiple input files.

## Description:
Processes multiple CSV input files and joins them together based on specified column criteria. This method orchestrates the entire CSV joining workflow, from input validation and file handling to table creation, join execution, and output generation. It supports various join types including inner, left, right, and outer joins with proper validation of join column specifications.

The method is called during the execution lifecycle of the CSVJoin utility when the run() method delegates to main() for the core processing logic. It handles command-line argument validation, file opening, CSV table creation using agate, and performs the actual join operations according to the specified join type.

## Args:
    self: The CSVJoin instance containing command-line arguments and utility configuration

## Returns:
    None: This method performs its work through side effects and does not return a value

## Raises:
    SystemExit: Raised via argparser.error() when validation fails for:
        - Missing input files when stdin is a TTY
        - Mismatch between join column count and input file count
        - Missing join columns for outer join operations
        - Conflicting join type flags (both left and right join specified)

## State Changes:
    Attributes READ:
        - self.args.input_paths: List of input file paths or '-' for stdin
        - self.args.columns: Join column specification string
        - self.args.left_join: Boolean flag for left join operation
        - self.args.right_join: Boolean flag for right join operation
        - self.args.outer_join: Boolean flag for outer join operation
        - self.args.skip_lines: Number of lines to skip at start of files
        - self.args.sniff_limit: Limit for CSV dialect detection
        - self.reader_kwargs: Keyword arguments for CSV reader configuration
        - self.writer_kwargs: Keyword arguments for CSV writer configuration
        - self.output_file: Output file handle for writing results
    
    Attributes WRITTEN:
        - self.input_files: List of opened file handles for input files

## Constraints:
    Preconditions:
        - self.args.input_paths must contain valid file paths or '-' for stdin
        - When stdin is a TTY, at least one input file must be specified
        - Join column specifications must be valid when required for join types
        - Only one join type flag can be specified at a time (left/right conflict)
        - For outer joins, join column names must be specified
    
    Postconditions:
        - All input files are properly opened and closed
        - Join operations are performed according to specified join type
        - Resulting joined table is written to output_file in CSV format
        - All temporary resources are cleaned up

## Side Effects:
    - Reads from multiple input files specified in self.args.input_paths
    - Writes joined CSV data to self.output_file
    - Opens and closes file handles for input files
    - May raise SystemExit for invalid command-line arguments
    - Uses agate.Table.join() for performing join operations
    - Uses agate.Table.from_csv() for creating table objects from CSV files
    - Uses match_column_identifier() for resolving column names to indices
    - Uses _parse_join_column_names() for parsing column specification strings
    - Uses _open_input_file() for opening input files
    - Uses get_column_types() for determining column data types

### `csvkit.utilities.csvjoin.CSVJoin._parse_join_column_names` · *method*

## Summary:
Parses a comma-separated string of column names into a list of stripped column name strings for join operations.

## Description:
Converts a comma-delimited string of column identifiers into a list of individual column names with leading/trailing whitespace removed. This method processes the --columns command-line argument which specifies which columns to join CSV files on.

This method is called during the CSV join operation setup phase, specifically when processing user-specified join column names from the command line interface. The parsed column names are later validated and resolved to actual column indices using match_column_identifier for the actual join operation.

## Args:
    join_string (str): A comma-separated string containing column names to join on. Each column name may have leading or trailing whitespace. Must not be None.

## Returns:
    list[str]: A list of column name strings with all leading and trailing whitespace removed from each element. Empty strings may appear in the result if the input contains consecutive commas or trailing commas.

## Raises:
    AttributeError: If join_string is None (though this would be a programming error as the caller ensures this is a string).

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - join_string must be a valid string (not None)
        - join_string should contain valid column name identifiers separated by commas
        
    Postconditions:
        - Returns a list of strings with no empty elements (unless the input contained empty elements)
        - All returned strings have leading/trailing whitespace stripped
        - The returned list preserves the order of columns as specified in the input string

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only processes string data and returns a transformed list.

## `csvkit.utilities.csvjoin.launch_new_instance` · *function*

## Summary:
Creates and executes a CSVJoin utility instance to perform SQL-like JOIN operations on multiple CSV files.

## Description:
This function serves as the entry point for launching the CSVJoin command-line utility. It instantiates a CSVJoin object and invokes its run() method to execute the JOIN operation on specified CSV files. The function encapsulates the boilerplate setup required to initialize and execute the CSVJoin utility, providing a clean interface for launching the tool from other modules or scripts.

This function is part of the standard csvkit utility pattern where each command-line tool provides a launch_new_instance() function to facilitate instantiation and execution. The CSVJoin utility specifically enables merging multiple CSV datasets based on common column values using SQL-like JOIN operations.

## Args:
    None

## Returns:
    None

## Raises:
    SystemExit: Raised by CSVJoin.run() when argument validation fails or when the utility encounters fatal errors during execution
    UnicodeDecodeError: Propagated from file reading operations when encoding issues occur
    ColumnIdentifierError: Raised by match_column_identifier() when column names/indices are invalid during JOIN column resolution
    ValueError: May be raised by argument parsing when invalid values are provided for numeric arguments

## Constraints:
    Preconditions:
        - Command-line arguments must be properly formatted for CSVJoin utility
        - Input CSV files must be readable and valid
        - JOIN column specifications (when provided) must reference valid columns in the input files
    
    Postconditions:
        - All input files are properly opened and closed
        - Output is written to the designated output stream/file
        - Memory is properly managed during CSV table processing

## Side Effects:
    - Reads input CSV files from disk
    - Writes output CSV data to stdout or specified output file
    - May raise SystemExit for invalid command-line arguments
    - Uses global stdin/stdout for I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[Create CSVJoin instance]
    B --> C[Call CSVJoin.run()]
    C --> D[Validate arguments via argparser]
    C --> E[Open input files]
    C --> F[Read CSV data into memory]
    C --> G[Perform JOIN operation]
    G --> H[Write result to output]
```

## Examples:
```python
# Typical usage from command-line (via csvkit)
csvjoin -c id file1.csv file2.csv > merged_output.csv

# Programmatic usage
from csvkit.utilities.csvjoin import launch_new_instance
launch_new_instance()  # Uses sys.argv by default
```

