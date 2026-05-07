# `in2csv.py`

## `csvkit.utilities.in2csv.In2CSV` · *class*

## Summary:
Converts common but less-awesome tabular data formats to CSV format.

## Description:
The In2CSV class is a command-line utility that transforms various structured data formats into CSV (Comma-Separated Values) format. It serves as a bridge between different data storage formats and CSV, making it easier to work with tabular data in spreadsheet applications or other tools that expect CSV input. This utility supports conversion from formats such as Excel (.xls, .xlsx), fixed-width files, JSON, DBF, GeoJSON, and NDJSON to CSV.

The class inherits from CSVKitUtility and implements the standard command-line interface pattern for CSVKit utilities. It provides automatic format detection when possible and supports explicit format specification via command-line arguments.

## State:
- `description` (str): A descriptive string explaining the utility's purpose
- `epilog` (str): Additional help text about format-specific command-line flags  
- `override_flags` (list): List of flag names that are overridden in this utility (specifically 'f' for format)
- `input_file`: File handle for reading the input data (set during execution)
- `output_file`: File handle for writing the output CSV data (set during execution)
- `args`: Parsed command-line arguments containing user-specified options (set during execution)

## Lifecycle:
Creation: The class is instantiated as part of the CSVKit command-line interface framework. It is not meant to be instantiated directly by application code but rather through the CLI entry point.
Usage: The main() method orchestrates the conversion process by:
1. Parsing command-line arguments through add_arguments()
2. Detecting or determining the input file format (automatic detection or explicit specification)
3. Opening appropriate input files based on format
4. Processing the data according to format-specific logic
5. Writing the result to the output file
6. Handling optional sheet writing operations when --write-sheets is specified
Destruction: The class automatically closes input and output files during cleanup in the main() method.

## Method Map:
```mermaid
graph TD
    A[main] --> B[add_arguments]
    B --> C[Parse arguments]
    C --> D{Format specified?}
    D -->|Yes| E[Use specified format]
    D -->|No| F[Detect format from file extension]
    E --> G{Names only requested?}
    G -->|Yes| H[Display sheet names and exit]
    G -->|No| I[Continue processing]
    I --> J{Format type}
    J -->|csv| K[agate.csv.reader/writer]
    J -->|json| L[agate.Table.from_json]
    J -->|ndjson| M[agate.Table.from_json with newline=True]
    J -->|xls|xlsx|N[agate.Table.from_xls/xlsx]
    J -->|dbf| O[agate.Table.from_dbf]
    J -->|fixed| P[fixed2csv converter]
    J -->|geojson| Q[geojson2csv converter]
    K --> R[Write to output]
    L --> R
    M --> R
    N --> R
    O --> R
    P --> R
    Q --> R
    R --> S[Handle write_sheets option]
    S --> T[Close input file]
```

## Raises:
- `ValueError`: Raised when schema is required for fixed-width files but not provided, or when DBF files are attempted to be read from stdin
- `argparse.ArgumentError`: Raised by argparser.error() when invalid combinations of arguments are provided (e.g., missing format for piped input)
- `IOError`: May be raised during file operations when files cannot be opened or read

## Example:
```python
# Convert an Excel file to CSV
in2csv input.xlsx > output.csv

# Convert a fixed-width file with schema
in2csv -f fixed -s schema.csv input.txt > output.csv

# Display sheet names from an Excel file
in2csv -n input.xlsx

# Convert JSON to CSV with a specific key
in2csv -f json -k "data" input.json > output.csv

# Convert XLS with specific encoding
in2csv --encoding-xls utf-16 input.xls > output.csv

# Write individual sheets to separate CSV files
in2csv --write-sheets "Sheet1,Sheet2" input.xlsx
```

### `csvkit.utilities.in2csv.In2CSV.add_arguments` · *method*

## Summary:
Configures command-line argument parser with all input format options for converting tabular data to CSV.

## Description:
This method registers all available command-line arguments with the In2CSV utility's argument parser. It enables users to specify input file format, handle various data sources (CSV, Excel, fixed-width, JSON), and configure conversion behavior such as sniffing limits and type inference. The method is part of the standard CSVKit utility pattern where argument parsing is separated from execution logic.

## Args:
    self: The In2CSV instance whose argparser will be configured

## Returns:
    None: This method modifies the instance's argparser in-place

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (configured with command-line arguments)

## Constraints:
    Preconditions: 
    - The method assumes self.argparser exists and is a proper ArgumentParser instance
    - SUPPORTED_FORMATS constant must be defined in the module scope and contain valid format identifiers
    
    Postconditions:
    - The argparser will have all standard in2csv command-line arguments registered
    - All argument validation rules are established for input file handling

## Side Effects:
    None: This method only configures the argument parser and doesn't perform I/O operations or modify external state

## Arguments Added:
- FILE (positional): Input file path, optional; accepts piped data via STDIN when omitted
- -f, --format: Specify input file format (choices limited to SUPPORTED_FORMATS); auto-detected if omitted
- -s, --schema: Schema file for fixed-width conversions (required when format is 'fixed')
- -k, --key: Top-level key for JSON processing (used when format is 'json')
- -n, --names: Display Excel sheet names only (valid for Excel files only)
- --sheet: Specific Excel sheet to process (valid for Excel files only)
- --write-sheets: Write Excel sheets to separate CSV files (valid for Excel files only)
- --use-sheet-names: Use sheet names as output filenames when writing sheets (requires --write-sheets)
- --encoding-xls: Specify encoding for XLS files (valid for Excel files only)
- -y, --snifflimit: Limit CSV dialect sniffing to specified bytes (0 to disable, -1 for full file)
- -I, --no-inference: Disable type inference and related options when parsing CSV

### `csvkit.utilities.in2csv.In2CSV.open_excel_input_file` · *method*

## Summary:
Opens an Excel input file for processing, returning a file-like object suitable for Excel format readers.

## Description:
This method provides a standardized way to open Excel input files (both .xls and .xlsx formats) for processing. It handles two special cases: when the input path is '-' (indicating stdin) or when no path is provided, it returns a BytesIO object containing the stdin buffer. For regular file paths, it opens the file in binary read mode and returns the file object. This method is primarily used by the In2CSV class to prepare input files for Excel-specific processing.

## Args:
    path (str): Path to the Excel file, or '-' to indicate stdin, or None/empty string for default behavior.

## Returns:
    file-like object: A BytesIO object when reading from stdin, or a file object opened in binary read mode for regular files.

## Raises:
    IOError: When the file cannot be opened for reading in binary mode.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The path parameter should be a valid file path, '-', or None/empty string
        - When using stdin ('-'), the method assumes standard input is available
    Postconditions:
        - Returns a file-like object that can be read by Excel processing functions
        - The returned object maintains proper binary reading capabilities

## Side Effects:
    - May read from standard input when path is '-'
    - Opens files in binary read mode for regular file paths
    - Creates BytesIO objects for stdin handling

### `csvkit.utilities.in2csv.In2CSV.sheet_names` · *method*

## Summary:
Retrieves the names of all sheets from an Excel file (either .xls or .xlsx format).

## Description:
This method extracts and returns the names of all worksheets contained within an Excel file. It handles both legacy .xls files (using xlrd library) and modern .xlsx files (using openpyxl library). The method is typically called when users want to see available sheet names or when preparing to process specific sheets from an Excel workbook.

## Args:
    path (str): Path to the Excel file to read sheet names from.
    filetype (str): The type of Excel file, either 'xls' for legacy format or 'xlsx' for modern format.

## Returns:
    list[str]: A list of strings representing the names of all sheets in the Excel workbook.

## Raises:
    Exception: May raise exceptions from file I/O operations or Excel library functions when opening/reading the file.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The path parameter must point to a valid Excel file
        - The filetype parameter must be either 'xls' or 'xlsx'
    Postconditions:
        - The input file is properly closed after reading
        - Returns a list of sheet names in the order they appear in the workbook

## Side Effects:
    - Opens and closes the Excel file for reading
    - Reads the entire file contents into memory temporarily
    - May read from standard input if path is '-'

### `csvkit.utilities.in2csv.In2CSV.main` · *method*

## Summary:
Converts input files from various formats (CSV, Excel, JSON, DBF, etc.) to CSV format, handling different file types and command-line options.

## Description:
This method serves as the primary entry point for the in2csv utility, processing input files of various formats and converting them to CSV format. It determines the input file type based on command-line arguments or automatic detection, opens appropriate input streams, processes the data according to format-specific logic, and writes the result to the output file. The method supports various command-line options including format specification, schema files, sheet selection, and special modes like --names-only.

## Args:
    self: The In2CSV instance containing command-line arguments and configuration

## Returns:
    None: This method performs I/O operations and does not return a meaningful value

## Raises:
    ValueError: When schema is required for fixed-format files or when DBF files are read from stdin
    SystemExit: When command-line argument validation fails (via argparser.error)

## State Changes:
    Attributes READ: 
        - self.args.input_path
        - self.args.filetype
        - self.args.schema
        - self.args.key
        - self.args.names_only
        - self.args.sniff_limit
        - self.args.no_header_row
        - self.args.skip_lines
        - self.args.no_inference
        - self.args.write_sheets
        - self.args.use_sheet_names
        - self.args.sheet
        - self.args.encoding_xls
        - self.reader_kwargs
        - self.writer_kwargs
        - self.argparser
    Attributes WRITTEN:
        - self.input_file
        - self.output_file

## Constraints:
    Preconditions:
        - Input file path must be specified when not reading from stdin
        - Schema file must be provided when converting fixed-width files
        - DBF files cannot be converted from stdin (must be a filename)
        - Excel sheet names must be valid when specified
    Postconditions:
        - Output file contains properly formatted CSV data
        - Input file handles are properly closed
        - Schema file handle is properly closed when used

## Side Effects:
    - Reads from input file(s) based on format
    - Writes to output file in CSV format
    - May create additional CSV files when --write-sheets option is used
    - Opens and closes file handles for input and schema files
    - Calls external libraries (agate, agatedbf, agateexcel) for format conversion

## `csvkit.utilities.in2csv.launch_new_instance` · *function*

## Summary:
Creates and executes a new instance of the In2CSV command-line utility.

## Description:
The launch_new_instance function serves as the entry point for launching the In2CSV utility from command-line contexts. It instantiates an In2CSV object and invokes its run() method to process command-line arguments and perform the actual conversion from various tabular data formats to CSV format.

This function is typically called by the CSVKit command-line framework when the in2csv utility is invoked. It follows the standard pattern of creating a utility instance and executing it, allowing the underlying In2CSV class to handle all argument parsing, format detection, and data conversion logic.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised by this function, though the underlying In2CSV.run() method may raise exceptions such as:
    - ValueError: When format requirements are not met or invalid arguments are provided
    - IOError: When file operations fail during input/output processing
    - argparse.ArgumentError: When command-line argument validation fails

## Constraints:
    Preconditions:
    - Command-line arguments must be available in sys.argv for argument parsing
    - The environment must support standard file I/O operations
    - Required input files must be accessible if specified
    
    Postconditions:
    - The utility processes input data according to command-line specifications
    - Output is written to stdout or the specified output file
    - All temporary resources are properly cleaned up

## Side Effects:
    - Reads from standard input or specified input files
    - Writes to standard output or specified output files
    - May read from or write to disk depending on command-line arguments
    - Processes command-line arguments from sys.argv

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance() called] --> B[Create In2CSV instance]
    B --> C[Call utility.run()]
    C --> D{In2CSV.run() executes}
    D --> E[Argument parsing occurs]
    E --> F[Input file opened if needed]
    F --> G[Format detection/selection]
    G --> H{Format-specific processing}
    H --> I[Data conversion to CSV]
    I --> J[Output written to destination]
    J --> K[Files closed]
    K --> L[Function returns]
```

## Examples:
```bash
# Typical usage from command line
in2csv input.xlsx > output.csv

# With explicit format specification
in2csv -f json input.json > output.csv

# Display sheet names only
in2csv -n input.xlsx
```

