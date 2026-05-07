# `csvlook.py`

## `csvkit.utilities.csvlook.CSVLook` · *class*

## Summary:
CSVLook is a command-line utility that renders CSV data as a formatted Markdown-compatible table in the console.

## Description:
CSVLook is a subclass of CSVKitUtility designed to display CSV data in a human-readable tabular format. It provides a command-line interface for quickly inspecting CSV files by rendering them as formatted tables in the terminal. The utility supports various formatting options such as limiting displayed rows/columns, truncating wide columns, and controlling numeric precision.

## State:
- description (str): Class-level attribute describing the utility's purpose
- argparser (argparse.ArgumentParser): Inherited from CSVKitUtility, configured with common CSV arguments plus CSVLook-specific arguments
- args (argparse.Namespace): Parsed command-line arguments containing user preferences
- input_file (file-like object): Inherited from CSVKitUtility, opened for reading CSV data
- output_file (file-like object): Inherited from CSVKitUtility, opened for writing formatted output

## Lifecycle:
- Creation: Instantiate with optional command-line arguments or file handles
- Usage: Call run() method which:
  1. Parses command-line arguments via add_arguments()
  2. Validates input requirements
  3. Reads CSV data using agate.Table.from_csv()
  4. Formats and prints the table using agate.Table.print_table()
- Destruction: Automatic cleanup handled by CSVKitUtility's run() method

## Method Map:
```mermaid
graph TD
    A[CSVLook.run] --> B{additional_input_expected?}
    B -->|Yes| C[error: 'You must provide an input file or piped data']
    B -->|No| D[Set kwargs dict]
    D --> E{max_precision set?}
    E -->|Yes| F[kwargs['max_precision'] = args.max_precision]
    E -->|No| G[Skip]
    F --> H{no_number_ellipsis set?}
    H -->|Yes| I[config.set_option('number_truncation_chars', '')]
    H -->|No| J[Skip]
    I --> K[sniff_limit = args.sniff_limit if != -1 else None]
    K --> L[agate.Table.from_csv()]
    L --> M[table.print_table()]
    M --> N[End]
```

## Raises:
- SystemExit: Raised by argparser.error() when no input file is provided
- Various exceptions: May raise exceptions from agate.Table.from_csv() or agate.Table.print_table() when encountering malformed data or I/O errors

## Example:
```bash
# Display CSV with default formatting
csvlook data.csv

# Limit to first 10 rows and 5 columns
csvlook --max-rows 10 --max-columns 5 data.csv

# Truncate columns wider than 20 characters
csvlook --max-column-width 20 data.csv

# Show only 2 decimal places for numbers
csvlook --max-precision 2 data.csv
```

### `csvkit.utilities.csvlook.CSVLook.add_arguments` · *method*

## Summary:
Adds command-line arguments to configure CSV display formatting and parsing behavior for the csvlook utility.

## Description:
This method extends the argument parser with options that control how CSV data is displayed and parsed. It defines various formatting parameters such as row/column limits, column width restrictions, numeric precision controls, and CSV dialect sniffing settings. These arguments allow users to customize the presentation of tabular data in a formatted table view, making large datasets more manageable and readable.

The method adds the following arguments to the parser:
- --max-rows: Limits the number of rows displayed before truncating
- --max-columns: Limits the number of columns displayed before truncating  
- --max-column-width: Truncates columns to a maximum width with ellipsis
- --max-precision: Controls decimal places displayed for numeric values
- --no-number-ellipsis: Disables ellipsis for numeric precision exceeding max-precision
- -y/--snifflimit: Controls CSV dialect sniffing behavior
- -I/--no-inference: Disables type inference during CSV parsing

## Args:
    self: The CSVLook instance whose argparser will be modified

## Returns:
    None: This method modifies the instance's argparser in-place

## Raises:
    None: This method does not raise exceptions directly

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modified in-place with new arguments)

## Constraints:
    Preconditions: The instance must have an initialized argparser attribute
    Postconditions: The argparser will contain all specified command-line arguments for CSV display control

## Side Effects:
    None: This method only modifies the argument parser object and has no external I/O or side effects

### `csvkit.utilities.csvlook.CSVLook.main` · *method*

## Summary:
Processes CSV input and displays it in a formatted table view with configurable output limits and formatting options.

## Description:
This method serves as the core execution logic for the csvlook utility, which converts CSV data into a nicely formatted table display. It validates input requirements, configures CSV parsing parameters, reads the CSV data into an agate Table object, and then prints the formatted table to the output stream. The method integrates with the CSVKitUtility base class lifecycle by being called during the run() execution phase after input file setup.

The method handles various CSV formatting options including precision control for numeric values, truncation character customization, row/column limits, and column width restrictions. It also supports advanced features like skipping initial lines, enabling line numbers, and custom column type inference. The method ensures that input is properly validated before processing and raises a SystemExit error if no input is provided.

## Args:
    self: The instance of CSVLook utility class

## Returns:
    None: This method does not return a value

## Raises:
    SystemExit: Raised via self.argparser.error when no input file or piped data is provided

## State Changes:
    Attributes READ: 
        - self.args.max_precision
        - self.args.no_number_ellipsis
        - self.args.sniff_limit
        - self.args.skip_lines
        - self.args.line_numbers
        - self.args.max_rows
        - self.args.max_columns
        - self.args.max_column_width
        - self.args.input_path
        - self.reader_kwargs
        - self.input_file
        - self.output_file
    Attributes WRITTEN: 
        - None

## Constraints:
    Preconditions:
        - self.args must be initialized with all expected attributes
        - Input file must be available via self.input_file or stdin must be connected
        - self.additional_input_expected() must return False to avoid SystemExit
        - All argument validation must have been completed by the parent run() method
        - self.input_file must be properly opened and accessible
        
    Postconditions:
        - CSV data is parsed and displayed in tabular format
        - Output is written to self.output_file
        - No modifications are made to the object's state

## Side Effects:
    - Reads from self.input_file (which could be a file or stdin)
    - Writes formatted table output to self.output_file
    - Configures global agate settings via agate.config.set_option()
    - Calls agate.Table.from_csv() to parse CSV data
    - Calls table.print_table() to render and output the formatted table

## `csvkit.utilities.csvlook.launch_new_instance` · *function*

## Summary:
Creates and executes a new instance of the CSVLook utility to render CSV data as a formatted table in the console.

## Description:
This function serves as the entry point for launching the CSVLook command-line utility. It instantiates a CSVLook object and invokes its run method to process CSV input and display it as a formatted Markdown-compatible table. The function encapsulates the basic workflow of creating a utility instance and executing it, providing a clean interface for utility initialization.

## Args:
    This function takes no arguments.

## Returns:
    This function does not return any value.

## Raises:
    SystemExit: Raised by CSVLook.run() when no input file is provided or when invalid arguments are supplied.
    Various exceptions: May propagate exceptions from agate.Table.from_csv() or agate.Table.print_table() when encountering malformed data or I/O errors.

## Constraints:
    Preconditions:
    - The function assumes that the command-line environment is properly set up with available arguments.
    - Input data must be accessible either through stdin/pipes or as a file argument.
    
    Postconditions:
    - The CSV data will be rendered as a formatted table in the console output.
    - Command-line arguments will be parsed and validated.

## Side Effects:
    - Writes formatted table output to stdout.
    - May read from stdin or file input depending on command-line arguments.
    - May raise SystemExit if validation fails.

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance] --> B[Create CSVLook instance]
    B --> C[Call utility.run()]
    C --> D[Parse arguments]
    D --> E{Input validation}
    E -->|Invalid| F[raise SystemExit]
    E -->|Valid| G[Process CSV data]
    G --> H[Render table]
    H --> I[Output to stdout]
```

## Examples:
```bash
# Launch CSVLook with default settings
python -c "from csvkit.utilities.csvlook import launch_new_instance; launch_new_instance()"

# Typical usage through command line
csvlook data.csv
```

