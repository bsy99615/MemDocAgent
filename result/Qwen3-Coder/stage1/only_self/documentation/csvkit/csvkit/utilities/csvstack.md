# `csvstack.py`

## `csvkit.utilities.csvstack._skip_lines` · *function*

## Summary:
Skips a specified number of lines from a file handle, typically used to bypass header rows or comment lines in CSV files.

## Description:
This helper function reads and discards a specified number of lines from a file handle. It's commonly used in CSV processing utilities to skip header rows, comment lines, or other non-data lines before processing the actual CSV content. The function validates that the skip_lines argument is an integer and raises a ValueError if not.

The function is typically called during the preprocessing phase of CSV file handling, before the main CSV parsing logic begins. It's particularly useful in utilities like csvstack where multiple CSV files need to be processed with consistent line-skipping behavior.

## Args:
    f (file-like object): A file handle from which lines will be read and discarded
    args (object): An arguments object containing a skip_lines attribute that specifies how many lines to skip

## Returns:
    int: The number of lines that were skipped, which corresponds to the value of args.skip_lines

## Raises:
    ValueError: When args.skip_lines is not an integer type

## Constraints:
    Preconditions:
    - The file handle `f` must be opened in read mode and be seekable
    - The args object must have a skip_lines attribute
    - The skip_lines value must be a non-negative integer
    
    Postconditions:
    - The file handle position will be advanced by the number of lines skipped
    - The skip_lines attribute in args remains unchanged

## Side Effects:
    - Reads from the file handle, advancing its position
    - May cause I/O operations on the underlying file

## Control Flow:
```mermaid
flowchart TD
    A[Start _skip_lines] --> B{isinstance(skip_lines, int)?}
    B -- Yes --> C[Initialize skip_lines counter]
    C --> D[while skip_lines > 0]
    D --> E[f.readline()]
    E --> F[skip_lines -= 1]
    F --> D
    D -- Exit loop --> G[Return skip_lines]
    B -- No --> H[Raise ValueError]
```

## Examples:
```python
# Typical usage in a CSV processing context
import csvkit.utilities.csvstack as csvstack

# Assuming we have a file handle and parsed arguments
with open('data.csv', 'r') as f:
    # Skip first 2 lines (header and metadata)
    args.skip_lines = 2
    lines_skipped = csvstack._skip_lines(f, args)
    # File pointer is now positioned at the start of actual data
```

## `csvkit.utilities.csvstack.CSVStack` · *class*

## Summary:
A command-line utility that stacks rows from multiple CSV files into a single output, optionally adding grouping information to distinguish source files.

## Description:
CSVStack is designed to combine multiple CSV files by vertically concatenating their rows while maintaining consistent column structure. It supports various grouping mechanisms to identify which source file each row originated from, making it useful for batch processing and data consolidation tasks.

This utility is particularly valuable when working with datasets that are split across multiple files but share the same schema. It handles both regular files and standard input, and provides flexible options for managing headers and grouping information.

The utility overrides several common CSV processing flags ('f', 'L', 'blanks', 'date-format', 'datetime-format') from the parent CSVKitUtility class, allowing for specialized behavior in stacking operations.

## State:
- `description` (str): Class variable describing the utility's purpose
- `override_flags` (list): List of argument flags overridden from parent class - ['f', 'L', 'blanks', 'date-format', 'datetime-format']
- `argparser`: Argument parser instance inherited from CSVKitUtility
- `args`: Parsed command-line arguments
- `output_file`: Output file handle for writing results
- `input_file`: Input file handle (inherited from CSVKitUtility)
- `reader_kwargs`: Keyword arguments for CSV reader construction
- `writer_kwargs`: Keyword arguments for CSV writer construction

## Lifecycle:
Creation: Instantiate with command-line arguments. The constructor initializes the argument parser and sets up standard CSV processing capabilities through CSVKitUtility parent class.

Usage: Call `run()` method which:
1. Processes input files sequentially
2. Handles header detection and column alignment
3. Applies grouping logic if specified
4. Writes combined output to the output file

Destruction: Automatic cleanup occurs through the parent class's run() method which properly closes file handles.

## Method Map:
```mermaid
graph TD
    A[run()] --> B[main()]
    B --> C[Validate grouping arguments]
    C --> D[Process input files for header detection]
    D --> E[Build unified header structure]
    E --> F[Write output header row]
    F --> G[Process each file row by row]
    G --> H[Apply grouping if needed]
    H --> I[Write row to output]
    I --> J[Close file handles]
```

## Raises:
- SystemExit: Raised by argparser.error() when grouping values don't match input files
- ValueError: Raised by _skip_lines() when skip_lines argument is not an integer
- UnicodeDecodeError: Handled by parent class exception handler for encoding issues

## Example:
```python
# Stack multiple CSV files with explicit grouping values
# Input files: sales_q1.csv, sales_q2.csv, sales_q3.csv
# Output will have a 'group' column indicating source file
csvstack sales_q1.csv sales_q2.csv sales_q3.csv -g "Q1,Q2,Q3" -n "quarter"

# Stack files using filenames as grouping values  
# Input files: data_2023.csv, data_2024.csv
# Output will have 'group' column with filenames as values
csvstack *.csv --filenames

# Stack from stdin with default group name
echo "name,age\nJohn,25" | csvstack -n "source"

# Stack files without headers (creates default column names)
csvstack file1.csv file2.csv --no-header-row
```

### `csvkit.utilities.csvstack.CSVStack.add_arguments` · *method*

## Summary:
Configures command-line arguments for the CSV stack utility, defining input file handling and grouping options.

## Description:
This method sets up the argument parser with command-line options for specifying input CSV files and configuring how grouping information is added to the stacked output. It's part of the CSVKitUtility framework and follows the standard pattern for CLI argument configuration in this codebase.

The method is called during the initialization phase of the CSV stack utility to define available command-line flags and their behaviors. It's separated from the main execution logic to maintain clean separation of concerns between argument parsing and business logic.

## Args:
    self: The CSVStack instance containing the argument parser to configure

## Returns:
    None: This method modifies the instance's argument parser in-place and returns nothing

## Raises:
    None: This method doesn't raise exceptions directly, though argument validation occurs later during parsing

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies the argument parser instance)

## Constraints:
    Preconditions: The method assumes self.argparser exists and is a proper ArgumentParser instance
    Postconditions: The argument parser is configured with the expected command-line options for CSV stacking

## Side Effects:
    None: This method only configures the argument parser and doesn't perform I/O operations or modify external state

### `csvkit.utilities.csvstack.CSVStack.main` · *method*

## Summary:
Processes multiple CSV input files and writes their combined content to output, optionally adding group identifiers to distinguish rows from different input files.

## Description:
The main method implements the core CSV stacking functionality by sequentially processing each input file, reading its content, and writing it to the output stream. It supports various CSV formats including header-preserving and headerless files, and provides optional grouping capabilities to track the origin of each row.

When stdin ('-') is specified as the only input and no data is piped, the method displays a warning message to stderr. The method intelligently handles both header-preserving CSV files (using DictReader) and headerless CSV files (using regular reader), collecting and merging headers appropriately. Grouping can be specified explicitly via --groups or automatically derived from input filenames via --group-by-filenames.

## Args:
    self: The CSVStack instance containing configuration and state

## Returns:
    None: This method performs I/O operations and does not return a value

## Raises:
    SystemExit: Raised via argparser.error() when the number of grouping values doesn't match input file count
    IOError: Raised by file operations when input files cannot be opened or read
    UnicodeDecodeError: Raised by CSV readers when encoding issues occur

## State Changes:
    Attributes READ:
    - self.args.input_paths: List of input file paths to stack
    - self.args.groups: Optional comma-separated group values for each input file
    - self.args.group_by_filenames: Boolean flag indicating if filenames should be used as group names
    - self.args.group_name: Optional custom name for the group column
    - self.args.no_header_row: Boolean flag indicating if input files lack header rows
    - self.args.skip_lines: Number of lines to skip at beginning of files
    - self.argparser: Argument parser instance for error reporting
    - self.output_file: Output file handle for writing results
    - self.reader_kwargs: Keyword arguments for CSV reader creation
    - self.writer_kwargs: Keyword arguments for CSV writer creation

    Attributes WRITTEN:
    - None: This method doesn't modify instance attributes directly

## Constraints:
    Preconditions:
    - self.args.input_paths must contain at least one file path
    - When using --groups, the number of group values must match the number of input files
    - Input files must be readable or stdin must be available for piping
    - CSV reader/writer configurations must be valid

    Postconditions:
    - All input files are processed and their content written to output
    - Output file contains properly formatted stacked CSV data
    - Group column (if enabled) is correctly inserted with appropriate values
    - Header row is written to output when applicable

## Side Effects:
    - Writes to stdout or specified output file
    - Reads from multiple input files or stdin
    - May display warning message to stderr when waiting for stdin input
    - Opens and closes file handles for input files
    - Performs I/O operations on filesystem and standard streams

## `csvkit.utilities.csvstack.launch_new_instance` · *function*

## Summary:
Creates and executes a new CSVStack utility instance to vertically concatenate rows from multiple CSV files.

## Description:
This function serves as the primary entry point for launching the CSVStack command-line utility. It instantiates a CSVStack object and invokes its run() method to process command-line arguments and execute the CSV stacking functionality. The function follows the standard csvkit pattern where command-line utilities are instantiated and executed through a dedicated launch function.

This logic is extracted into its own function rather than being inlined in the main module to enable:
- Consistent instantiation pattern across different invocation contexts
- Testability of the utility creation and execution flow
- Separation of concerns between utility creation and execution
- Support for alternative launch mechanisms (like in unit tests or other entry points)

The CSVStack utility combines multiple CSV files by vertically concatenating their rows while maintaining consistent column structure. It supports various grouping mechanisms to identify which source file each row originated from, making it useful for batch processing and data consolidation tasks.

## Args:
    None

## Returns:
    None

## Raises:
    SystemExit: Raised by CSVStack.run() when argument validation fails or when the utility encounters fatal errors during execution
    Various exceptions from file I/O operations handled by the parent CSVKitUtility class
    ValueError: Raised by _skip_lines() when skip_lines argument is not an integer
    UnicodeDecodeError: Potentially raised during CSV reading if encoding issues occur (handled by parent class)

## Constraints:
    Preconditions:
    - Command-line arguments must be available via sys.argv for parsing
    - Standard input/output streams must be accessible
    - Required CSV processing dependencies must be available
    - Input files (if specified) must be readable
    
    Postconditions:
    - A CSVStack utility instance is created and executed
    - Multiple CSV files are processed and stacked into a single output
    - Grouping information is added to distinguish source files if specified
    - All temporary resources are properly cleaned up

## Side Effects:
    - Reads from standard input or specified input files (via CSVKitUtility's input_file handling)
    - Writes stacked CSV output to standard output or specified output file (via CSVKitUtility's output_file handling)
    - Processes command-line arguments from sys.argv through CSVKitUtility's argument parser
    - May display usage information or error messages to stderr

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[Create CSVStack() instance]
    B --> C[Call utility.run()]
    C --> D{Input file handling}
    D -->|File specified| E[Open input file]
    D -->|No file| F[Use stdin]
    E --> G[Parse command-line arguments]
    F --> G
    G --> H{Validation checks}
    H -->|Invalid args| I[Display error and exit]
    H -->|Valid args| J[Process CSV data]
    J --> K[Process input files for header detection]
    K --> L[Build unified header structure]
    L --> M[Write output header row]
    M --> N[Process each file row by row]
    N --> O[Apply grouping if needed]
    O --> P[Write row to output]
    P --> Q[Close file handles]
    Q --> R[Return completion status]
```

## Examples:
```bash
# Stack multiple CSV files with explicit grouping values
# Input files: sales_q1.csv, sales_q2.csv, sales_q3.csv
# Output will have a 'group' column indicating source file
csvstack sales_q1.csv sales_q2.csv sales_q3.csv -g "Q1,Q2,Q3" -n "quarter"

# Stack files using filenames as grouping values  
# Input files: data_2023.csv, data_2024.csv
# Output will have 'group' column with filenames as values
csvstack *.csv --filenames

# Stack from stdin with default group name
echo "name,age\nJohn,25" | csvstack -n "source"

# Stack files without headers (creates default column names)
csvstack file1.csv file2.csv --no-header-row
```

