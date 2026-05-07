# `csvlook.py`

## `csvkit.utilities.csvlook.CSVLook` · *class*

## Summary:
Renders CSV data as a Markdown-compatible, fixed-width table in the console.

## Description:
The CSVLook utility formats and displays CSV data in a readable tabular format suitable for console output. It is designed to be used as a command-line tool for quickly viewing CSV files in a structured, aligned format that's compatible with Markdown tables. This class extends CSVKitUtility to provide CSV-specific formatting capabilities.

## State:
- `description`: Class attribute describing the utility's purpose (immutable string)
- `argparser`: Argument parser instance inherited from CSVKitUtility (created during initialization)
- `args`: Parsed command-line arguments (set during initialization)
- `input_file`: Input file handle (opened during execution)
- `output_file`: Output file handle (defaults to stdout)
- `reader_kwargs`: CSV reader configuration parameters (inherited from CSVKitUtility)
- `writer_kwargs`: CSV writer configuration parameters (inherited from CSVKitUtility)

## Lifecycle:
- Creation: Instantiated by the CSVKit framework when invoked as a command-line utility
- Usage: Called via the `run()` method inherited from CSVKitUtility, which internally calls `main()`
- Destruction: Automatically closes input file handle during cleanup phase

## Method Map:
```mermaid
graph TD
    A[CSVLook.run()] --> B[CSVLook.main()]
    B --> C[CSVLook.additional_input_expected()]
    C --> D{Input Expected?}
    D -->|No| E[CSVLook.argparser.error()]
    D -->|Yes| F[agate.Table.from_csv()]
    F --> G[agate.Table.print_table()]
```

## Raises:
- `SystemExit`: Raised by `argparser.error()` when no input file is provided
- `UnicodeDecodeError`: Propagated from file operations when encoding issues occur
- `ValueError`: May be raised during argument parsing or file operations

## Example:
```bash
# Display CSV file with default formatting
csvlook data.csv

# Limit displayed rows and columns
csvlook --max-rows 10 --max-columns 5 data.csv

# Truncate long columns and limit decimal precision
csvlook --max-column-width 20 --max-precision 2 data.csv
```

### `csvkit.utilities.csvlook.CSVLook.add_arguments` · *method*

## Summary:
Configures command-line arguments for the csvlook utility to control CSV display formatting and parsing behavior.

## Description:
This method extends the base CSVKitUtility argument parser by adding specific command-line options for the csvlook utility. It enables users to customize how CSV data is rendered as a Markdown-compatible table in the console, including controlling display limits, column width, number precision, and CSV parsing behavior. The method is called during the initialization phase of the CSVLook utility to set up all available command-line options.

## Args:
    self: The CSVLook instance whose argument parser is being configured

## Returns:
    None: This method modifies the instance's argument parser in-place and returns nothing

## Raises:
    None: This method does not raise exceptions directly

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies the argument parser instance)

## Constraints:
    Preconditions: 
    - The method must be called on a CSVLook instance that has been initialized
    - The instance must have a valid argparser attribute (inherited from CSVKitUtility)
    
    Postconditions:
    - The argparser instance contains all the defined command-line arguments
    - All argument defaults and help text are properly configured

## Side Effects:
    None: This method only modifies the internal argument parser configuration and has no external side effects

## Arguments Added:
- --max-rows: Limits the number of rows displayed before truncating the data
- --max-columns: Limits the number of columns displayed before truncating the data  
- --max-column-width: Truncates columns to specified width, replacing remainder with ellipsis
- --max-precision: Controls decimal places displayed for numeric values, replacing excess with ellipsis
- --no-number-ellipsis: Disables ellipsis when max-precision is exceeded for numeric values
- -y/--snifflimit: Controls CSV dialect sniffing limit in bytes (0 to disable, -1 to sniff entire file)
- -I/--no-inference: Disables type inference when parsing input, disabling value reformatting

### `csvkit.utilities.csvlook.CSVLook.main` · *method*

## Summary:
Processes CSV input and renders it as a formatted Markdown-compatible table in the console.

## Description:
This method serves as the core execution logic for the csvlook utility, which converts CSV data into a human-readable, fixed-width table format suitable for console output and Markdown documentation. It validates input requirements, configures number formatting options, parses CSV data using the agate library with appropriate type inference, and outputs the formatted table to the designated output stream.

The method is called by the parent class's `run()` method as part of the standard CSVKit utility execution lifecycle. It performs input validation to ensure data is available (either from a file or piped input), applies user-configured formatting options, and leverages agate's robust CSV parsing capabilities to handle various CSV dialects and data types.

## Args:
    self: The CSVLook instance containing parsed command-line arguments and utility configuration.

## Returns:
    None: This method does not return a value directly, but produces formatted table output to the configured output file.

## Raises:
    SystemExit: Raised by self.argparser.error() when no input file is provided and stdin is connected to a terminal (interactive mode).

## State Changes:
    Attributes READ:
    - self.args.max_precision: Controls decimal precision formatting
    - self.args.no_number_ellipsis: Determines whether to apply number truncation ellipsis
    - self.args.sniff_limit: Controls CSV dialect sniffing limit
    - self.args.skip_lines: Specifies number of initial lines to skip
    - self.args.line_numbers: Indicates whether to include line numbers in output
    - self.args.max_rows: Limits displayed rows
    - self.args.max_columns: Limits displayed columns
    - self.args.max_column_width: Truncates column widths
    - self.reader_kwargs: Contains CSV reader configuration parameters
    - self.input_file: Source of CSV data
    - self.output_file: Destination for formatted table output
    
    Attributes WRITTEN:
    - None: This method doesn't modify instance attributes directly

## Constraints:
    Preconditions:
    - Command-line arguments must be parsed and available via self.args
    - Input file must be accessible or stdin must be available for piped data
    - The CSVKitUtility parent class must be properly initialized
    
    Postconditions:
    - Formatted table output is written to self.output_file
    - CSV data is parsed with appropriate type inference
    - Number formatting options are applied according to user configuration

## Side Effects:
    - Reads from self.input_file (CSV source)
    - Writes formatted table output to self.output_file (console or file)
    - Modifies global agate configuration via config.set_option() when --no-number-ellipsis is specified
    - May reconfigure stdin encoding when reading from standard input
    - Calls agate.Table.from_csv() which may perform file I/O and parsing operations
    - Calls table.print_table() which performs output formatting and writing

## `csvkit.utilities.csvlook.launch_new_instance` · *function*

## Summary:
Creates and executes a CSVLook utility instance to render CSV data as a formatted table in the console.

## Description:
This function serves as the entry point for launching the CSVLook command-line utility. It instantiates a CSVLook class and invokes its run method to process CSV input and display it in a Markdown-compatible, fixed-width table format. The function encapsulates the instantiation and execution workflow, providing a clean interface for utility startup.

The CSVLook utility is designed to be used as a command-line tool for quickly viewing CSV files in a structured, aligned format that's compatible with Markdown tables. It extends CSVKitUtility to provide CSV-specific formatting capabilities.

## Args:
    None

## Returns:
    None

## Raises:
    SystemExit: Raised by CSVLook's argument parser when no input file is provided or invalid arguments are given
    UnicodeDecodeError: Propagated from file operations when encoding issues occur during CSV processing
    ValueError: May be raised during argument parsing or file operations within CSVLook

## Constraints:
    Preconditions:
    - Command-line arguments must be available for parsing (typically provided by the CLI framework)
    - Either a file path must be provided as input or data must be piped via stdin
    - Valid CSV data must be available for processing
    
    Postconditions:
    - CSV data is rendered as a formatted table to stdout
    - Input file handle is properly closed after processing
    - Command-line arguments are parsed and validated

## Side Effects:
    - Reads from stdin or specified input file
    - Writes formatted table output to stdout
    - May read from command-line arguments for configuration
    - May raise SystemExit when validation fails

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[CSVLook()]
    B --> C[utility.run()]
    C --> D{Input Provided?}
    D -->|No| E[SystemExit]
    D -->|Yes| F[agate.Table.from_csv()]
    F --> G[agate.Table.print_table()]
    G --> H[Output to stdout]
```

## Examples:
```bash
# Basic usage - display CSV file
csvlook data.csv

# Pipe data to csvlook
echo "a,b,c\n1,2,3" | csvlook

# With custom options
csvlook --max-rows 10 --max-columns 5 data.csv
```

