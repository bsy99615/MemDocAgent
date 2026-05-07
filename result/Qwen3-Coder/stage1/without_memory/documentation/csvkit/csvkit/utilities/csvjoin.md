# `csvjoin.py`

## `csvkit.utilities.csvjoin.CSVJoin` · *class*

## Summary:
A command-line utility that executes SQL-like joins to merge multiple CSV files based on specified column(s).

## Description:
The CSVJoin class provides functionality to perform database-style join operations on multiple CSV files. It supports various join types including inner, left, right, and full outer joins. The class is designed to be used as a command-line utility that processes CSV files and outputs the joined result to standard output or a specified file. It inherits from CSVKitUtility, which provides common CLI argument handling and file I/O capabilities.

This class is particularly useful for combining data from multiple CSV sources based on common identifiers, such as IDs or keys, making it valuable for data integration and analysis workflows.

## State:
- `input_files`: List of opened file objects for each input CSV file
- `args`: Parsed command-line arguments containing join configuration
- `output_file`: Output file handle for writing the joined results
- `reader_kwargs`: Keyword arguments for CSV reader configuration
- `writer_kwargs`: Keyword arguments for CSV writer configuration

Initialization parameters:
- `args`: Command-line arguments (optional, defaults to None)
- `output_file`: Output file handle (optional, defaults to sys.stdout)

## Lifecycle:
Creation: Instantiate CSVJoin with optional arguments and output file. The constructor automatically parses command-line arguments and sets up the argument parser.

Usage: Call the `run()` method to execute the join operation. The class internally calls `main()` which:
1. Validates input files and arguments
2. Opens and reads all input CSV files into memory using agate.Table
3. Performs the appropriate join operation based on specified flags
4. Writes the resulting joined table to the output file

Destruction: Files are automatically closed during processing, and no explicit cleanup is required.

## Method Map:
```mermaid
graph TD
    A[CSVJoin.run()] --> B[CSVJoin.main()]
    B --> C[Validate input paths]
    B --> D[Open input files]
    B --> E[Parse join columns]
    B --> F[Read CSV files into agate.Tables]
    B --> G[Perform join operation]
    B --> H[Write result to output]
    G --> I[agate.Table.join()]
```

## Raises:
- `argparse.ArgumentTypeError`: When invalid join column specifications are provided
- `SystemExit`: When validation fails and argparse.error() is called
- `ValueError`: When invalid column identifiers are encountered
- `IOError`: When input files cannot be opened or read

## Example:
```python
# Join two CSV files on a common column
# csvjoin -c id file1.csv file2.csv > joined_output.csv

# Perform a left outer join
# csvjoin --left -c id file1.csv file2.csv > left_joined_output.csv

# Join multiple files with different join columns
# csvjoin -c "id,name" file1.csv file2.csv file3.csv > multi_joined_output.csv
```

### `csvkit.utilities.csvjoin.CSVJoin.add_arguments` · *method*

## Summary:
Configures command-line argument parser with CSV join operation options.

## Description:
This method initializes the argument parser with all available command-line options for joining CSV files. It defines positional arguments for input files and optional arguments for specifying join columns, join types (inner, outer, left, right), CSV parsing parameters like sniff limit, and type inference controls. This method is called during the initialization of the CSVJoin utility to set up the command-line interface.

## Args:
    None - this is an instance method that modifies self.argparser

## Returns:
    None - modifies self.argparser in-place to add command-line arguments

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (adds multiple argument definitions to the parser)

## Constraints:
    Preconditions: 
    - self.argparser must be initialized and accessible
    - This method should only be called during object initialization/setup phase
    
    Postconditions:
    - self.argparser contains all defined command-line arguments for CSV joining
    - Each argument has proper help text, default values, and validation settings

## Side Effects:
    None - only modifies internal argument parser configuration

### `csvkit.utilities.csvjoin.CSVJoin.main` · *method*

## Summary:
Joins multiple CSV files together using specified column-based join operations.

## Description:
Processes multiple input CSV files and performs various types of SQL-style joins (inner, left, right, outer) on them based on specified join columns. The joined result is written to the output file.

## Args:
    self: The CSVJoin instance containing configuration and state

## Returns:
    None: This method performs I/O operations and does not return a value

## Raises:
    SystemExit: When validation errors occur due to invalid command-line arguments

## State Changes:
    Attributes READ: self.args, self.argparser, self.input_files, self.output_file, self.reader_kwargs, self.writer_kwargs
    Attributes WRITTEN: self.input_files (populated with opened file handles)

## Constraints:
    Preconditions:
    - Input paths must be valid or stdin must not be a TTY when using '-' as input
    - For outer joins, join column names must be specified
    - Cannot specify both left and right join simultaneously
    - Number of join column names must match number of input files or be a single column name existing in all files
    
    Postconditions:
    - All input files are closed after processing
    - Output file contains the joined CSV data

## Side Effects:
    - Reads from multiple input file paths or stdin
    - Writes to output file
    - May raise SystemExit for invalid argument combinations

### `csvkit.utilities.csvjoin.CSVJoin._parse_join_column_names` · *method*

## Summary:
Parses a comma-separated string of column names into a list of stripped column name strings.

## Description:
This method processes a string containing column names separated by commas and returns a list of those column names with leading and trailing whitespace removed. It is used to parse the join column specification provided by the user via the --columns command-line argument.

The method is called during the main execution flow when join column names are specified, allowing the CSV join utility to properly identify which columns to use for joining multiple CSV files.

## Args:
    join_string (str): A comma-separated string of column names to be parsed.

## Returns:
    list[str]: A list of column name strings with leading and trailing whitespace removed.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The join_string parameter must be a valid string.
    Postconditions: The returned list contains exactly one entry for each comma-separated component in the input string, with all whitespace stripped.

## Side Effects:
    None.

## `csvkit.utilities.csvjoin.launch_new_instance` · *function*

*No documentation generated.*

