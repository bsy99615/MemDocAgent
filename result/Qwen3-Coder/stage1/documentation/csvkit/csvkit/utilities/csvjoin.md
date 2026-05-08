# `csvjoin.py`

## `csvkit.utilities.csvjoin.CSVJoin` · *class*

## Summary:
A command-line utility for executing SQL-like joins on multiple CSV files based on specified column(s).

## Description:
The CSVJoin class implements a command-line utility that merges multiple CSV files using SQL-like join operations. It supports inner, left, right, and full outer joins on one or more columns, allowing users to combine data from multiple CSV files based on matching values in specified columns.

This utility is particularly useful for combining datasets that share common identifiers or keys, such as joining customer data with order data based on customer IDs. The class follows the CSVKit framework pattern for command-line utilities, inheriting standard CSV parsing and argument handling capabilities.

## State:
- `input_files`: List of opened file handles for input CSV files, populated during main() execution
- `args`: Parsed command-line arguments containing join configuration, inherited from CSVKitUtility.parent
- `output_file`: Output file handle for writing the joined result, inherited from CSVKitUtility.parent
- Inherits all state from CSVKitUtility parent class including:
  - `argparser`: Argument parser instance for command-line interface
  - `reader_kwargs`: CSV reader configuration parameters (delimiter, quoting, etc.)
  - `writer_kwargs`: CSV writer configuration parameters (line numbers, etc.)

## Lifecycle:
- Creation: Instantiated automatically by CSVKit framework when invoked from command line via CSVKitUtility.__init__()
- Usage: Called via CSVKitUtility.run() which internally calls main() method
- Destruction: Automatic cleanup of file handles occurs after execution through CSVKitUtility framework

## Method Map:
```mermaid
flowchart TD
    A[main()] --> B[Validate arguments]
    B --> C[Open input files]
    C --> D[Parse join columns]
    D --> E[Read CSV files into agate.Tables]
    E --> F[Determine join type]
    F --> G[Perform join operations]
    G --> H[Write result to output]
    B --> I{Invalid args?}
    I -- Yes --> J[Exit with error]
    I -- No --> F
```

## Raises:
- `ArgumentParserError`: Raised when invalid argument combinations are provided:
  - Conflicting join types (--left and --right specified together)
  - Missing join columns for outer joins (--outer, --left, or --right without --columns)
  - Mismatch between number of join columns and input files
- `FileNotFoundError`: Raised when input files cannot be opened
- `ValueError`: Raised when column identifiers are invalid or out of bounds
- `ColumnIdentifierError`: Raised by match_column_identifier when column names/positions are invalid

## Example:
```bash
# Join two CSV files on a common column
csvjoin -c id file1.csv file2.csv > joined_output.csv

# Perform a left outer join
csvjoin --left -c name users.csv orders.csv > left_joined.csv

# Join multiple files with different join columns
csvjoin -c "id,product_id,category_id" file1.csv file2.csv file3.csv > multi_joined.csv

# Perform full outer join without specifying columns
csvjoin --outer file1.csv file2.csv > outer_joined.csv
```

### `csvkit.utilities.csvjoin.CSVJoin.add_arguments` · *method*

## Summary:
Configures command-line arguments for the CSV join utility, defining input files, join columns, join types, and CSV parsing options.

## Description:
This method initializes the argument parser with various command-line options specific to joining CSV files. It defines positional arguments for input files, optional arguments for specifying join columns and join types (inner, outer, left, right), and CSV parsing configuration options. This method is part of the CSVJoin class that extends CSVKitUtility and implements the add_arguments abstract method required by the base class.

## Args:
    self: The CSVJoin instance whose argument parser is being configured.

## Returns:
    None: This method modifies the instance's argument parser in-place and does not return a value.

## Raises:
    None: This method does not raise exceptions directly, though argument parsing may raise exceptions during execution.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (configured with various arguments)

## Constraints:
    Preconditions: The method assumes self.argparser exists and is an ArgumentParser instance.
    Postconditions: The self.argparser instance is populated with command-line argument definitions for CSV joining operations.

## Side Effects:
    None: This method only configures the argument parser and does not perform I/O operations or modify external state.

### `csvkit.utilities.csvjoin.CSVJoin.main` · *method*

## Summary
Joins multiple CSV files together using specified column-based or sequential joining strategies, writing the result to the output file.

## Description
This method orchestrates the CSV joining process by opening input files, parsing join column specifications, loading CSV data into agate Tables, performing the appropriate join operation based on command-line flags, and writing the merged result to the output file. It handles various join types including inner, left, right, and outer joins, with validation for proper usage of join columns and join flags.

## Args
    None (uses self.args and self.output_file from the class instance)

## Returns
    None (writes result to self.output_file)

## Raises
    SystemExit: When validation fails due to invalid command-line arguments, such as:
        - Missing input files when stdin is a TTY
        - Mismatch between number of join columns and input files
        - Missing join columns when performing outer joins
        - Conflicting join flags (both left and right joins specified)
    argparse.ArgumentTypeError: When argument parsing fails

## State Changes
    Attributes READ: 
        - self.args.input_paths
        - self.args.columns
        - self.args.left_join
        - self.args.right_join
        - self.args.outer_join
        - self.args.sniff_limit
        - self.args.skip_lines
        - self.args.no_inference
        - self.args.date_format
        - self.args.datetime_format
        - self.args.locale
        - self.args.blanks
        - self.args.null_values
        - self.args.zero_based
        - self.output_file
        - self.reader_kwargs
        - self.writer_kwargs
    Attributes WRITTEN:
        - self.input_files (temporary storage during execution)

## Constraints
    Preconditions:
        - Command-line arguments must be properly parsed and validated
        - Input files must be readable or stdin must be available for piped data
        - Join column specifications must be valid when required for outer joins
        - Only one join type flag can be specified at a time (left, right, or outer)
        
    Postconditions:
        - All input files are properly opened and closed
        - CSV data is loaded into agate Table objects
        - Proper join operation is performed based on flags
        - Result is written to the output file with appropriate formatting

## Side Effects
    - Opens and closes multiple input files from self.args.input_paths
    - Reads data from stdin when no input files are specified
    - Writes merged CSV data to self.output_file
    - May raise SystemExit for invalid argument combinations
    - Uses agate.Table.from_csv() to parse CSV files
    - Uses agate.Table.join() to perform join operations
    - Uses agate.Table.to_csv() to write output

### `csvkit.utilities.csvjoin.CSVJoin._parse_join_column_names` · *method*

## Summary
Parses a comma-separated string of column names into a list, removing leading/trailing whitespace from each name.

## Description
This method processes the join column specification provided by users via the --columns command-line argument. It splits the input string on commas and strips whitespace from each resulting column name to normalize the input format. This normalization ensures consistent handling of column names regardless of spacing in the user's input.

The method is called during the CSV join operation setup phase when validating and preparing join column specifications for further processing by the CSVJoin class.

## Args
    join_string (str): A comma-separated string containing column names to be joined on. Each column name may have leading or trailing whitespace.

## Returns
    list[str]: A list of column names with whitespace stripped from each element. Empty strings are preserved if they result from consecutive commas or trailing commas.

## Raises
    None

## State Changes
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints
    Preconditions:
        - join_string must be a valid string
        - join_string may contain comma-separated column names with optional whitespace
        
    Postconditions:
        - Returns a list of strings with leading/trailing whitespace removed from each element
        - The returned list preserves the order of column names as specified in the input
        - Empty strings may be present in the returned list if the input contains consecutive commas or trailing commas

## Side Effects
    None

## `csvkit.utilities.csvjoin.launch_new_instance` · *function*

## Summary:
Creates and executes a CSVJoin command-line utility instance to perform SQL-like joins on multiple CSV files.

## Description:
This function serves as the entry point for launching the CSVJoin command-line utility. It instantiates a CSVJoin object and invokes its run() method to process command-line arguments and execute the join operation on specified CSV files. This function follows the CSVKit framework pattern where utilities are launched through a standardized initialization and execution sequence.

The function is typically called by the CSVKit framework when the csvjoin command is executed from the command line, either directly or through the main CLI entry point. It encapsulates the instantiation and execution workflow for the CSVJoin utility.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised by this function, though the underlying CSVJoin.run() method may raise various exceptions during execution including:
    - ArgumentParserError: When invalid argument combinations are provided
    - FileNotFoundError: When input files cannot be opened
    - ValueError: When column identifiers are invalid or out of bounds
    - ColumnIdentifierError: When column names/positions are invalid

## Constraints:
    - Preconditions: The function assumes that the CSVKit framework environment is properly initialized and that command-line arguments are available
    - Postconditions: The function completes execution after the CSVJoin utility finishes processing

## Side Effects:
    - Reads input CSV files specified in command-line arguments
    - Writes output to stdout or specified output file
    - May raise system exceptions if file operations fail
    - Uses standard input/output streams for I/O operations

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[Create CSVJoin instance]
    B --> C[Call utility.run()]
    C --> D{utility.run() completes}
    D --> E[Return]
```

## Examples:
```bash
# Direct usage through command line
csvjoin -c id file1.csv file2.csv > output.csv

# Using the function programmatically (though typically called by framework)
from csvkit.utilities.csvjoin import launch_new_instance
launch_new_instance()
```

