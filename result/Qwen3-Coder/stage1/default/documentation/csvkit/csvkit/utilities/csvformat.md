# `csvformat.py`

## `csvkit.utilities.csvformat.CSVFormat` · *class*

*No documentation generated.*

### `csvkit.utilities.csvformat.CSVFormat.add_arguments` · *method*

## Summary:
Configures command-line arguments for CSV formatting options including header control, delimiter specification, quoting styles, and line termination settings.

## Description:
Adds command-line argument definitions to the utility's argument parser for controlling CSV output formatting. This method is part of the CSVKitUtility base class pattern where subclasses implement add_arguments() to extend command-line interface with domain-specific options.

The method configures various CSV formatting parameters that affect how output CSV files are written, including header row behavior, field delimiters, quote characters, quoting styles, escape characters, and line terminators.

## Args:
    self: The CSVFormat instance whose argparser will be modified

## Returns:
    None: This method modifies the instance's argparser in-place and returns nothing

## Raises:
    None: This method does not raise exceptions directly

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modified in-place with new argument definitions)

## Constraints:
    Preconditions: 
    - self.argparser must be initialized (typically happens during CSVKitUtility.__init__)
    - The method should only be called during argument parser setup phase
    
    Postconditions:
    - Command-line arguments for CSV formatting are registered with self.argparser
    - Parsed arguments will be available as attributes on self.args after parsing

## Side Effects:
    None: This method only registers argument definitions with the argument parser and does not perform I/O or modify external state

### `csvkit.utilities.csvformat.CSVFormat._extract_csv_writer_kwargs` · *method*

*No documentation generated.*

### `csvkit.utilities.csvformat.CSVFormat.main` · *method*

## Summary:
Formats and outputs CSV data with configurable header handling and line skipping options.

## Description:
Processes input CSV data according to command-line arguments and writes the formatted output to the designated output file. This method implements the core CSV formatting logic for the csvformat utility, handling various options such as skipping initial lines, managing header rows, and applying custom CSV reader/writer configurations.

The method is designed as a standalone entry point that orchestrates the CSV processing workflow by:
1. Checking if additional input is expected from stdin
2. Setting up CSV readers and writers with appropriate configurations
3. Handling special header row scenarios (no header row, skip header)
4. Writing the processed CSV data to output

This logic is encapsulated in its own method rather than being inlined because it represents the complete execution flow for the CSV formatting utility, coordinating multiple CSV processing operations while maintaining clean separation of concerns.

## Args:
    None (uses self.args for command-line argument access)

## Returns:
    None (performs I/O operations directly)

## Raises:
    None explicitly raised by this method (relies on underlying CSV operations)

## State Changes:
    Attributes READ: 
        - self.args: Command-line arguments controlling CSV processing behavior
        - self.reader_kwargs: Configuration for CSV reader construction
        - self.writer_kwargs: Configuration for CSV writer construction
        - self.output_file: Destination for formatted CSV output
    Attributes WRITTEN: 
        - None (modifies external state through I/O operations)

## Constraints:
    Preconditions:
        - The CSVKitUtility instance must be properly initialized with input/output handles
        - Command-line arguments must be parsed and available in self.args
        - Reader and writer kwargs must be properly configured
        - Output file must be writable
    Postconditions:
        - Formatted CSV data is written to self.output_file
        - All input data is processed according to specified options

## Side Effects:
    I/O Operations: 
        - Reads from input file or stdin via self.skip_lines() and agate.csv.reader
        - Writes to output file via agate.csv.writer
        - Writes informational message to stderr when waiting for stdin input
    External Dependencies: 
        - Uses agate.csv.reader and agate.csv.writer for CSV processing
        - Relies on sys.stderr for status messages
        - Depends on itertools.chain for header manipulation

## `csvkit.utilities.csvformat.launch_new_instance` · *function*

## Summary:
Creates and executes a CSVFormat utility instance to convert CSV files to custom output formats.

## Description:
This function serves as the entry point for launching the CSVFormat utility. It instantiates a CSVFormat class and invokes its run() method to process CSV input according to specified formatting options. The function abstracts away the instantiation and execution details, providing a clean interface for starting the CSV conversion process.

The CSVFormat utility allows users to convert CSV files to different output formats with customizable delimiters, quoting styles, and other CSV formatting options. This function encapsulates the standard initialization and execution workflow for this utility.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised by this function, though the underlying CSVFormat.run() method may raise exceptions related to file I/O, argument parsing, or CSV processing errors.

## Constraints:
    Preconditions:
    - The csvkit library must be properly installed and importable
    - Command-line arguments must be properly set up before calling (typically handled by the CLI framework)
    - Standard input/output streams must be available for processing
    
    Postconditions:
    - The CSVFormat utility will have processed input according to its configuration
    - Any specified output will be written to the configured output destination
    - File handles will be properly closed after execution

## Side Effects:
    - Reads from standard input or specified input files
    - Writes to standard output or specified output files
    - May write informational messages to standard error
    - Processes command-line arguments through the argument parser

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance called] --> B[Create CSVFormat instance]
    B --> C[Call utility.run()]
    C --> D{run() executes}
    D -->|Success| E[CSV processing completes]
    D -->|Exception| F[Exception propagated]
    E --> G[Function returns]
    F --> G
```

## Examples:
```python
# Typical usage would be through command line:
# csvformat input.csv -D ';' -Q '"'

# Programmatic usage:
from csvkit.utilities.csvformat import launch_new_instance
launch_new_instance()
```

