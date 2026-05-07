# `csvlook.py`

## `csvkit.utilities.csvlook.CSVLook` · *class*

## Summary:
Renders CSV files as Markdown-compatible, fixed-width tables in the console.

## Description:
The CSVLook utility is designed to display CSV data in a formatted, readable table layout that's compatible with Markdown syntax. It's particularly useful for quickly inspecting CSV data in terminal environments. This class extends CSVKitUtility to provide standardized command-line argument handling and file I/O operations while implementing specific CSV rendering functionality.

The utility supports various formatting options including row/column limits, column width restrictions, and precision controls for numeric values. It can handle compressed files and provides intelligent CSV dialect detection.

## State:
- `description`: Class variable describing the utility's purpose (set to 'Render a CSV file in the console as a Markdown-compatible, fixed-width table.')
- `argparser`: Argument parser instance inherited from CSVKitUtility with standard CSV arguments plus custom arguments for display control
- `args`: Parsed command-line arguments containing display and processing options
- `output_file`: Output file handle (defaults to stdout) inherited from CSVKitUtility
- `input_file`: Input file handle inherited from CSVKitUtility
- `reader_kwargs`: Dictionary of keyword arguments for CSV reader construction inherited from CSVKitUtility

## Lifecycle:
Creation: Instantiate with optional command-line arguments. The constructor initializes the argument parser and parses command-line arguments through the parent CSVKitUtility.run() method.

Usage: The utility follows the standard CSVKitUtility execution flow:
1. Initialize via constructor with optional arguments
2. Call run() method to execute the utility (inherited from CSVKitUtility)
3. The run() method calls main() which performs the CSV processing and rendering
4. Output is written to the configured output_file

Destruction: Automatic cleanup occurs through the parent class's file handling mechanisms.

## Method Map:
```mermaid
graph TD
    A[run()] --> B[main()]
    B --> C[additional_input_expected()]
    B --> D[get_column_types()]
    B --> E[Table.from_csv()]
    E --> F[input_file]
    E --> G[reader_kwargs]
    E --> H[skip_lines]
    E --> I[column_types]
    E --> J[line_numbers]
    B --> K[table.print_table()]
    K --> L[output_file]
    K --> M[max_rows]
    K --> N[max_columns]
    K --> O[max_column_width]
    K --> P[max_precision]
```

## Raises:
- SystemExit: Raised by argparser.error() when no input file is provided (via additional_input_expected())
- Various exceptions from file I/O operations handled by parent CSVKitUtility
- UnicodeDecodeError: Potentially raised during CSV reading if encoding issues occur (handled by parent class)

## Example:
```python
# Basic usage
csvlook input.csv

# With display limitations
csvlook --max-rows 10 --max-columns 5 input.csv

# With precision control
csvlook --max-precision 2 input.csv

# With column width restriction
csvlook --max-column-width 20 input.csv

# Disable number ellipsis
csvlook --max-precision 2 --no-number-ellipsis input.csv

# Disable type inference
csvlook --no-inference input.csv

# Control CSV sniffing limit
csvlook --snifflimit 2048 input.csv
```

### `csvkit.utilities.csvlook.CSVLook.add_arguments` · *method*

## Summary:
Configures the command-line argument parser with display formatting options for CSV data.

## Description:
Adds multiple command-line arguments to the instance's argument parser that control how CSV data is displayed, including row/column limits, column width restrictions, precision settings, and CSV parsing behavior. This method encapsulates all argument configuration for the CSVLook utility, separating the CLI interface setup from the core functionality.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self.argparser
    Attributes WRITTEN: self.argparser (modified via add_argument calls)

## Constraints:
    Preconditions: The instance must have an argparser attribute initialized (typically done in the parent class)
    Postconditions: The argparser instance will contain all the defined command-line arguments

## Side Effects:
    Modifies the instance's argument parser by adding new arguments to it

### `csvkit.utilities.csvlook.CSVLook.main` · *method*

## Summary:
Processes CSV input and displays it in a formatted table layout with configurable display options.

## Description:
This method serves as the primary execution entry point for the csvlook utility, which reads CSV data from input and renders it in a visually formatted table. It validates input requirements, configures CSV processing parameters, reads the CSV data using agate's robust CSV parsing capabilities, and outputs a formatted representation to the specified output destination.

The method orchestrates the complete workflow of CSV table rendering, including input validation, configuration of number formatting, CSV parsing with support for various CSV dialects and encodings, and final table presentation with customizable display limits.

## Args:
    None: This method operates on the instance's internal state and command-line arguments.

## Returns:
    None: This method performs its work through side effects and does not return a value.

## Raises:
    SystemExit: Raised via argparser.error() when no input file is provided and stdin is not connected to a terminal.

## State Changes:
    Attributes READ: 
    - self.args: Parsed command-line arguments containing CSV processing options
    - self.input_file: File-like object containing the CSV data to process
    - self.output_file: File-like object where the formatted table will be written
    - self.reader_kwargs: Dictionary of CSV reader configuration parameters
    
    Attributes WRITTEN: 
    - None: This method does not modify any instance attributes directly

## Constraints:
    Preconditions:
    - The CSVKitUtility instance must have been properly initialized with parsed arguments
    - Either an input file path must be provided or data must be available on stdin
    - The input file must be readable and contain valid CSV data
    - All command-line arguments must be properly parsed
    
    Postconditions:
    - The CSV data is successfully parsed and rendered as a formatted table
    - Output is written to the configured output destination
    - Global configuration may be modified via agate.config.set_option() when --no-number-ellipsis is specified

## Side Effects:
    - Reads from self.input_file (which may involve file I/O or stdin)
    - Writes formatted table output to self.output_file
    - Modifies global configuration via agate.config.set_option() when --no-number-ellipsis is specified
    - Potentially reads from stdin if no input file is provided
    - May raise SystemExit if input validation fails

## `csvkit.utilities.csvlook.launch_new_instance` · *function*

## Summary:
Creates and executes a new CSVLook utility instance to render CSV files as Markdown-compatible tables in the console.

## Description:
This function serves as the primary entry point for launching the CSVLook command-line utility. It instantiates a CSVLook object and invokes its run() method to process CSV input and display it in a formatted, readable table layout. The function follows the standard csvkit pattern where command-line utilities are instantiated and executed through a dedicated launch function.

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
    SystemExit: Raised by CSVLook.run() when no input file is provided or when argument validation fails
    Various exceptions from file I/O operations handled by CSVKitUtility parent class
    UnicodeDecodeError: Potentially raised during CSV reading if encoding issues occur (handled by parent class)

## Constraints:
    Preconditions:
    - Command-line arguments must be available via sys.argv for parsing
    - Standard input/output streams must be accessible
    - Required CSV processing dependencies must be available
    - Input files (if specified) must be readable
    
    Postconditions:
    - A CSVLook utility instance is created and executed
    - CSV data is rendered as a Markdown-compatible table in the console
    - All temporary resources are properly cleaned up

## Side Effects:
    - Reads from standard input or specified input files (via CSVKitUtility's input_file handling)
    - Writes formatted table output to standard output (via CSVKitUtility's output_file handling)
    - Processes command-line arguments from sys.argv through CSVKitUtility's argument parser
    - May display usage information or error messages to stderr

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[Create CSVLook instance]
    B --> C[Call CSVLook.run()]
    C --> D{Input file handling}
    D -->|File specified| E[Open input file]
    D -->|No file| F[Use stdin]
    E --> G[Parse command-line arguments]
    F --> G
    G --> H{Validation checks}
    H -->|Invalid args| I[Display error and exit]
    H -->|Valid args| J[Process CSV data]
    J --> K[Render as Markdown table]
    K --> L[Write formatted output to stdout]
    L --> M[Cleanup and exit]
```

## Examples:
```bash
# Basic usage - render CSV from stdin
cat data.csv | csvlook

# Basic usage - render CSV from file
csvlook data.csv

# With display limitations
csvlook --max-rows 10 --max-columns 5 data.csv

# With precision control
csvlook --max-precision 2 data.csv

# With column width restriction
csvlook --max-column-width 20 data.csv
```

