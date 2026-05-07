# `in2csv.py`

## `csvkit.utilities.in2csv.In2CSV` · *class*

## Summary:
In2CSV is a command-line utility that converts various tabular data formats (such as Excel, JSON, DBF, and fixed-width files) into CSV format.

## Description:
In2CSV serves as a versatile converter for transforming structured data from numerous non-CSV formats into the widely-compatible CSV format. It is designed to be used as part of the csvkit command-line toolkit and inherits from CSVKitUtility, leveraging its argument parsing and file handling infrastructure. The utility automatically detects input file formats when possible, though users can explicitly specify formats using the --format option. It supports conversion of Excel files (both .xls and .xlsx), JSON data, fixed-width files, database files (.dbf), and GeoJSON data.

## State:
- input_file (file-like object): Input stream opened for reading the source data
- output_file (file-like object): Output stream for writing the resulting CSV data
- args (argparse.Namespace): Parsed command-line arguments containing conversion options
- reader_kwargs (dict): Configuration parameters for CSV readers
- writer_kwargs (dict): Configuration parameters for CSV writers

## Lifecycle:
- Creation: Instantiated with optional command-line arguments and output file handle
- Usage: Called via run() method which orchestrates:
  1. Argument parsing
  2. Input file opening (if needed)
  3. Format detection or specification
  4. Data conversion based on detected/format-specific logic
  5. Output writing to specified destination
  6. Cleanup of file handles
- Destruction: Automatic cleanup of input/output file handles occurs in the run() method

## Method Map:
```mermaid
graph TD
    A[In2CSV.run] --> B[In2CSV.add_arguments]
    B --> C[Parse arguments]
    C --> D{Format specified?}
    D -->|Yes| E[Set filetype]
    D -->|No| F[Guess format with convert.guess_format]
    F --> G{Names only requested?}
    G -->|Yes| H[Display sheet names]
    G -->|No| I[Open input file]
    I --> J{Filetype in ('xls','xlsx')?}
    J -->|Yes| K[Open Excel input file]
    J -->|No| L[Open regular input file]
    L --> M{Special handling needed?}
    M -->|Yes| N[Apply special processing]
    M -->|No| O[Prepare conversion kwargs]
    O --> P{Specific format conversion}
    P -->|CSV| Q[Use agate.Table.from_csv]
    P -->|JSON| R[Use agate.Table.from_json]
    P -->|Fixed| S[Use fixed2csv]
    P -->|GeoJSON| T[Use geojson2csv]
    P -->|XLS/XLSX| U[Use agate.Table.from_xls/from_xlsx]
    P -->|DBF| V[Use agate.Table.from_dbf]
    Q --> W[Write to CSV]
    R --> W
    S --> W
    T --> W
    U --> W
    V --> W
    W --> X[Handle write_sheets if specified]
    X --> Y[Cleanup]
```

## Raises:
- ValueError: Raised when schema is required for fixed-width files but not provided
- ValueError: Raised when DBF files are attempted to be read from stdin
- SystemExit: Raised by argparser.error() when invalid arguments are provided

## Example:
```python
# Convert Excel file to CSV
in2csv input.xlsx > output.csv

# Convert JSON to CSV with specific key
in2csv --format json --key records data.json > output.csv

# Convert fixed-width file with schema
in2csv --format fixed --schema schema.csv data.txt > output.csv

# Display sheet names from Excel file
in2csv --names input.xlsx

# Convert Excel file with specific sheet
in2csv --sheet Sheet1 input.xlsx > output.csv

# Convert Excel file and write sheets to separate files
in2csv --write-sheets Sheet1,Sheet2 input.xlsx
```

### `csvkit.utilities.in2csv.In2CSV.add_arguments` · *method*

*No documentation generated.*

### `csvkit.utilities.in2csv.In2CSV.open_excel_input_file` · *method*

## Summary:
Opens an Excel input file for reading, handling both file paths and standard input streams.

## Description:
This method provides a standardized way to open Excel files (both .xls and .xlsx formats) for processing. It handles two special cases: when the input path is None or '-', it reads from standard input and wraps it in a BytesIO object; otherwise, it opens the file in binary read mode. This method is specifically designed for Excel file handling within the In2CSV utility.

## Args:
    path (str): The file path to open, or None/empty string for stdin, or '-' for stdin

## Returns:
    BytesIO or file-like object: A readable file-like object containing the Excel file data

## Raises:
    IOError: When the file cannot be opened in binary read mode

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The path parameter should be a string, None, or empty string
    Postconditions: Returns either a BytesIO object (for stdin) or a file handle (for regular files)

## Side Effects:
    I/O operations: Reads from stdin when path is '-' or None, or opens a file when path is a valid file path

### `csvkit.utilities.in2csv.In2CSV.sheet_names` · *method*

## Summary:
Retrieves the names of all sheets from an Excel file, supporting both .xls and .xlsx formats.

## Description:
This method extracts sheet names from Excel files by opening them with appropriate libraries based on file type. It uses xlrd for .xls files and openpyxl for .xlsx files. The method is part of the In2CSV utility's Excel processing pipeline and is called during the sheet enumeration phase when users want to see available sheets before conversion. This method encapsulates the Excel file reading logic to avoid duplication and ensure consistent handling of both file formats.

## Args:
    path (str): File path to the Excel file, or None/empty string for stdin, or '-' for stdin
    filetype (str): File type identifier, either 'xls' or 'xlsx' (determines which library to use)

## Returns:
    list[str]: A list of sheet names contained in the Excel workbook

## Raises:
    IOError: When the file cannot be opened or read
    xlrd.XLRDError: When xlrd encounters issues parsing .xls files (such as corrupted files or unsupported features)
    openpyxl.utils.exceptions.InvalidFileException: When openpyxl encounters issues parsing .xlsx files (such as corrupted files or unsupported features)

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The path argument must be a valid file path or stdin indicator ('-' or None)
    - The filetype argument must be either 'xls' or 'xlsx' (though any other value defaults to 'xlsx')
    - The Excel file at path must be readable and valid
    Postconditions: 
    - Returns a list of sheet names in order they appear in the workbook
    - The input file is properly closed after reading

## Side Effects:
    I/O operations: Opens and reads from the specified Excel file
    External library calls: Uses xlrd or openpyxl depending on file type

### `csvkit.utilities.in2csv.In2CSV.main` · *method*

## Summary:
Processes input files of various formats (CSV, Excel, JSON, DBF, fixed-width, GeoJSON) and converts them to CSV format, supporting schema-based conversion, sheet extraction, and metadata display.

## Description:
The main method orchestrates the conversion of input files from various formats into CSV format. It determines the input file type based on extensions, command-line arguments, or automatic detection, then applies appropriate conversion logic. The method handles special cases like extracting sheet names (--names-only), processing Excel files with multiple sheets (--write-sheets), and applying schema-based conversions for fixed-width files. It leverages the agate library for most data processing operations and integrates with csvkit's specialized converters for fixed-width and GeoJSON formats.

This method is the core execution point for the in2csv utility, serving as the entry point that coordinates all file format detection, input handling, and conversion logic. It's designed to be called internally by the CSVKitUtility framework's run() method.

## Args:
    self: The In2CSV utility instance containing parsed arguments and configuration

## Returns:
    None: This method performs I/O operations and does not return a value

## Raises:
    ValueError: When schema is required for fixed-width format but not provided, or when DBF files are read from stdin
    SystemExit: When input file format cannot be determined, when required arguments are missing, or when invalid combinations are specified

## State Changes:
    Attributes READ:
        - self.args.input_path: Path to input file or '-' for stdin
        - self.args.filetype: Explicitly specified file type
        - self.args.schema: Path to schema file for fixed-width conversion
        - self.args.key: JSON key for nested data
        - self.args.names_only: Flag to display sheet names only
        - self.args.sniff_limit: Limit for CSV dialect detection
        - self.args.no_header_row: Flag to indicate no header row in input
        - self.args.skip_lines: Number of lines to skip at start of file
        - self.args.no_inference: Flag to disable data type inference
        - self.args.write_sheets: Flag to write all sheets to separate files
        - self.args.use_sheet_names: Flag to use sheet names in output filenames
        - self.args.sheet: Specific sheet to process
        - self.args.encoding_xls: Encoding for XLS files
        - self.argparser: Argument parser instance for error reporting
        - self.reader_kwargs: Configuration for CSV reader
        - self.writer_kwargs: Configuration for CSV writer
    Attributes WRITTEN:
        - self.input_file: Assigned based on file type and opened accordingly
        - self.output_file: Used for writing output CSV data

## Constraints:
    Preconditions:
        - Input file path must be valid or stdin must be piped with --format specified
        - Schema file must be provided when converting fixed-width files
        - DBF files cannot be processed from stdin (must be file paths)
        - Excel sheet names must be valid when using --write-sheets with specific sheet numbers
        - When using --names-only, input must be Excel file (.xls or .xlsx)
        - When using --write-sheets, input must be Excel file (.xls or .xlsx)
    Postconditions:
        - Input file is closed after processing
        - Output file contains properly formatted CSV data
        - Schema file is closed if opened (when applicable)
        - Additional output files may be created when --write-sheets is used

## Side Effects:
    - Opens and closes input/output files
    - Reads from input file streams
    - Writes to output file streams
    - May create additional output files when --write-sheets is used
    - Calls external functions from agate, csvkit.convert.fixed, and csvkit.convert.geojs
    - May raise SystemExit for argument validation errors

## `csvkit.utilities.in2csv.launch_new_instance` · *function*

## Summary:
Launches a new instance of the In2CSV utility to process and convert input data into CSV format.

## Description:
This function creates a new instance of the In2CSV class and executes its run method to perform the conversion process. It serves as the entry point for initiating the CSV conversion workflow from the command line interface. The function encapsulates the instantiation and execution of the In2CSV utility, providing a clean interface for launching the conversion process.

## Args:
    None

## Returns:
    None

## Raises:
    ValueError: Raised when schema is required for fixed-width files but not provided
    SystemExit: Raised by argparser.error() when invalid arguments are provided

## Constraints:
    Preconditions:
    - The In2CSV class must be properly defined and accessible
    - Command-line arguments must be available for parsing
    - Input/output file handles must be properly configured
    
    Postconditions:
    - The In2CSV utility's run method completes successfully or raises appropriate exceptions
    - All input/output file handles are properly managed and closed
    - Conversion results are written to the appropriate output destination

## Side Effects:
    - Creates a new In2CSV instance
    - Invokes the run method of the In2CSV utility
    - May perform file I/O operations (reading input files, writing output files)
    - May interact with standard input/output streams
    - May display help text or error messages to stderr/stdout

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance] --> B[Create In2CSV instance]
    B --> C[Call utility.run()]
    C --> D[In2CSV.run executes conversion]
    D --> E{Input validation}
    E -->|Valid| F[Process input file]
    E -->|Invalid| G[Raise exception]
    F --> H[Output file written]
    H --> I[Return]
```

## Examples:
```python
# Typical usage in command-line context
launch_new_instance()

# Equivalent to running:
# in2csv input_file > output_file
```

