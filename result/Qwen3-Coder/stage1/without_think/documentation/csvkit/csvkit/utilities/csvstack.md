# `csvstack.py`

## `csvkit.utilities.csvstack._skip_lines` · *function*

*No documentation generated.*

## `csvkit.utilities.csvstack.CSVStack` · *class*

*No documentation generated.*

### `csvkit.utilities.csvstack.CSVStack.add_arguments` · *method*

## Summary:
Configures command-line argument parsing for the csvstack utility to handle multiple CSV file stacking operations with optional grouping.

## Description:
This method sets up the argument parser with specific command-line options for the csvstack utility. It defines how users can specify input files, apply grouping factors, and control how grouping information is represented in the output. The method is part of the CSVKitUtility framework and follows the standard pattern of implementing argument configuration for command-line tools.

## Args:
    self: The CSVStack instance whose argument parser is being configured

## Returns:
    None: This method modifies the instance's argument parser in-place

## Raises:
    None explicitly raised: This method only configures arguments and doesn't raise exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies the argument parser instance)

## Constraints:
    Preconditions: The method assumes self.argparser exists and is an ArgumentParser instance
    Postconditions: The argument parser is properly configured with all required csvstack options

## Side Effects:
    None: This method only configures argument parsing and doesn't perform I/O or external service calls

### `csvkit.utilities.csvstack.CSVStack.main` · *method*

## Summary:
Stacks multiple CSV files into a single output file, optionally adding group identifiers to distinguish rows from different input files.

## Description:
This method implements the core logic for the csvstack utility, which combines multiple CSV files into a single output by concatenating their rows. It handles various configuration options including header row management, grouping of rows by input file, and proper CSV formatting. The method is invoked internally by the parent CSVKitUtility.run() method during execution of the csvstack command-line utility.

## Args:
    self: The CSVStack instance containing configuration and state information.

## Returns:
    None: This method performs I/O operations and does not return a value.

## Raises:
    SystemExit: Raised when the number of grouping values doesn't match the number of input files, causing the argument parser to exit with an error message.
    IOError: Raised when there are issues opening or reading input files.
    UnicodeDecodeError: Raised when input files cannot be decoded with the specified encoding.

## State Changes:
    Attributes READ: 
    - self.args.input_paths
    - self.args.groups
    - self.args.group_by_filenames
    - self.args.group_name
    - self.args.no_header_row
    - self.output_file
    - self.reader_kwargs
    - self.writer_kwargs
    - self.argparser
    
    Attributes WRITTEN: 
    - None: This method operates on the instance's attributes but doesn't modify them directly

## Constraints:
    Preconditions:
    - self.args.input_paths must contain valid file paths or '-' for stdin
    - If groups are specified, the number of group values must equal the number of input files
    - The output file must be writable
    - CSV reader/writer configurations must be valid
    
    Postconditions:
    - Output file contains concatenated rows from all input files
    - Header row is written if applicable
    - Group columns are added when requested
    - Input files are properly closed after processing

## Side Effects:
    - Writes to stdout or the specified output file
    - Reads from stdin when no input files are provided
    - Reads from multiple input files specified in self.args.input_paths
    - May write to stderr when waiting for stdin input
    - Opens and closes files using the _open_input_file helper method
    - Uses agate.csv readers and writers for CSV processing
    - Calls _skip_lines helper function to skip initial lines

## `csvkit.utilities.csvstack.launch_new_instance` · *function*

## Summary:
Launches a new instance of the CSVStack utility to stack rows from multiple CSV files.

## Description:
This function serves as the primary entry point for initializing and executing the CSVStack utility. It creates an instance of the CSVStack class and invokes its run() method to process CSV files according to the configured arguments. The function abstracts away the instantiation and execution details, providing a clean interface for launching the utility.

## Args:
    None

## Returns:
    None

## Raises:
    SystemExit: When command-line arguments are invalid or when the utility encounters fatal errors during processing.
    Exception: Various exceptions may be raised during file operations or argument parsing, though these are typically handled internally by the CSVKitUtility base class.

## Constraints:
    Preconditions:
    - The function assumes that command-line arguments are available via sys.argv or have been passed to the CSVStack constructor
    - The system must have appropriate permissions to read input files and write to output destinations
    
    Postconditions:
    - The utility processes input CSV files and produces stacked output to stdout or specified output file
    - Command-line argument validation occurs before processing begins

## Side Effects:
    - Reads from input CSV files or stdin
    - Writes processed CSV data to stdout or specified output file
    - May display error messages to stderr
    - Processes command-line arguments and modifies global state through argument parser

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance called] --> B[Create CSVStack instance]
    B --> C[Call utility.run()]
    C --> D[CSVKitUtility.run() executes]
    D --> E[Parse command-line arguments]
    E --> F[Open input files]
    F --> G[Validate arguments]
    G --> H{Arguments valid?}
    H -->|No| I[Show error and exit]
    H -->|Yes| J[Call CSVStack.main()]
    J --> K[Process CSV files]
    K --> L[Write output]
    L --> M[Return success]
```

## Examples:
```python
# Typical usage from command line:
# csvstack file1.csv file2.csv file3.csv

# Programmatic usage:
from csvkit.utilities.csvstack import launch_new_instance
launch_new_instance()
```

