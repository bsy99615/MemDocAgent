# `in2csv.py`

## `csvkit.utilities.in2csv.In2CSV` · *class*

## Summary:
Converts input files of various formats (CSV, Excel, DBF, JSON, GeoJSON, fixed-width) to CSV format, handling special cases like sheet enumeration and multi-sheet Excel files.

## Description:
The In2CSV class provides functionality to convert various tabular data formats into standard CSV format. It supports multiple input formats including Excel spreadsheets (.xls, .xlsx), fixed-width files, JSON, GeoJSON, and database files (.dbf). The class handles special cases such as enumerating Excel sheet names with the -n flag and writing multiple Excel sheets to separate CSV files with the --write-sheets option.

This class is part of the csvkit utilities framework and is designed to be used through the command-line interface, though it can also be used programmatically. It automatically detects file formats when possible and provides extensive configuration options for handling different input characteristics.

## State:
- `input_file`: File handle for the input data being processed (opened in main method)
- `output_file`: File handle for the output CSV data (inherited from parent)
- `args`: Parsed command-line arguments containing conversion options (inherited from parent)
- `reader_kwargs`: Keyword arguments for CSV reader configuration (inherited from parent)
- `writer_kwargs`: Keyword arguments for CSV writer configuration (inherited from parent)
- `override_flags`: Set to ['f'] indicating special handling of the -f/--format flag

The class inherits from CSVKitUtility which provides common argument parsing, file handling, and configuration capabilities.

## Lifecycle:
Creation: The class is instantiated with command-line arguments and initialized through the parent CSVKitUtility constructor. Arguments are parsed and validated.

Usage: The main conversion logic is executed through the `main()` method, which:
1. Determines the input file format (auto-detection or explicit specification)
2. Opens appropriate input file handles
3. Processes the input according to its format type
4. Writes converted data to the output file
5. Handles special operations like sheet enumeration (--names) and multi-sheet writing (--write-sheets)

Destruction: Input files are automatically closed during the execution of the `main()` method through the parent class cleanup mechanisms.

## Method Map:
```mermaid
graph TD
    A[In2CSV.main()] --> B[Format determination]
    B --> C{File type}
    C -->|Excel| D[open_excel_input_file]
    C -->|Other| E[_open_input_file]
    D --> F[sheet_names if -n flag]
    E --> G[Process conversion based on format]
    G --> H{Format type}
    H -->|CSV| I[agate.Table.from_csv]
    H -->|JSON| J[agate.Table.from_json]
    H -->|XLS| K[agate.Table.from_xls]
    H -->|XLSX| L[agate.Table.from_xlsx]
    H -->|DBF| M[agate.Table.from_dbf]
    H -->|Fixed| N[fixed2csv]
    H -->|GeoJSON| O[geojson2csv]
    I --> P[table.to_csv]
    J --> P
    K --> P
    L --> P
    M --> P
    N --> P
    O --> P
    P --> Q[Write to output_file]
    Q --> R{--write-sheets flag}
    R -->|Yes| S[Process multiple sheets]
    R -->|No| T[End]
```

## Raises:
- `argparse.ArgumentTypeError`: When invalid arguments are provided
- `ValueError`: When schema is required for fixed-width files but not provided, or when DBF files are read from stdin
- `SystemExit`: When argument validation fails (via argparser.error calls)
- `UnicodeDecodeError`: When input file encoding issues occur (handled by parent class)

## Example:
```python
# Typical command-line usage:
# in2csv input.xlsx > output.csv
# in2csv -f json input.json > output.csv
# in2csv --format csv input.txt > output.csv
# in2csv --names input.xlsx  # Display sheet names
# in2csv --write-sheets sheet1,input.xlsx > output.csv  # Write specific sheets

# Programmatic usage:
from csvkit.utilities.in2csv import In2CSV
import sys

# Create instance with arguments
utility = In2CSV(['input.xlsx'])
# Run the conversion
utility.run()
```

### `csvkit.utilities.in2csv.In2CSV.add_arguments` · *method*

## Summary:
Configures command-line argument parsers for the in2csv utility to support conversion of various tabular data formats to CSV.

## Description:
This method initializes the argument parser with all available command-line options for the in2csv utility, enabling users to convert various tabular data formats (CSV, Excel, fixed-width, JSON, etc.) to CSV format. It is part of the CSVKit command-line utility framework and is called during the initialization phase of the In2CSV tool to define available options and their behaviors.

## Args:
    self: The In2CSV instance whose argparser will be configured with command-line arguments.

## Returns:
    None: This method modifies the instance's argument parser in-place and returns nothing.

## Raises:
    None explicitly raised: This method configures arguments but doesn't raise exceptions itself.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies the argument parser instance to add various arguments)

## Constraints:
    Preconditions: The In2CSV instance must have an argparser attribute properly initialized (typically by the parent CSVKitUtility class).
    Postconditions: The argparser attribute will contain all configured command-line arguments for in2csv functionality.

## Side Effects:
    None: This method only configures the argument parser and doesn't perform I/O operations or modify external state.

## Arguments Added:
- FILE (positional, optional): The CSV file to operate on. If omitted, will accept input as piped data via STDIN.
- -f, --format: Specify the format of the input file. If not specified, will be inferred from the file type. Supported formats include those defined in SUPPORTED_FORMATS constant.
- -s, --schema: Specify a CSV-formatted schema file for converting fixed-width files.
- -k, --key: Specify a top-level key to look within for a list of objects to be converted when processing JSON.
- -n, --names: Display sheet names from the input Excel file.
- --sheet: Specify the name of the Excel sheet to operate on.
- --write-sheets: Specify the names of Excel sheets to write to files, or "-" to write all sheets.
- --use-sheet-names: Use the sheet names as file names when --write-sheets is set.
- --encoding-xls: Specify the encoding of the input XLS file.
- -y, --snifflimit: Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely, or "-1" to sniff the entire file.
- -I, --no-inference: Disable type inference (and --locale, --date-format, --datetime-format) when parsing CSV input.

## Usage Context:
This method is called automatically during the construction of In2CSV instances as part of the CSVKitUtility initialization process, ensuring that all command-line options are available before the utility executes.

### `csvkit.utilities.in2csv.In2CSV.open_excel_input_file` · *method*

## Summary:
Opens an Excel input file for reading, handling both standard file paths and stdin input.

## Description:
This method provides a standardized way to open Excel files (both .xls and .xlsx formats) for processing. When the input path is None, empty, or '-', it reads from standard input and wraps the content in a BytesIO object. For regular file paths, it opens the file in binary read mode. This abstraction allows the rest of the Excel processing pipeline to work uniformly with file-like objects regardless of the input source.

## Args:
    path (str): The file path to open, or None/empty string for stdin, or '-' for stdin.

## Returns:
    BytesIO or file object: A file-like object containing the Excel file data for reading.

## Raises:
    IOError: When the file cannot be opened for reading.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The path parameter should be a valid file path string or None/empty/'-' for stdin.
    Postconditions: Returns a file-like object that can be read from for Excel processing.

## Side Effects:
    I/O: Reads from stdin when path is '-' or None/empty, or from a file when path is a valid file path.

### `csvkit.utilities.in2csv.In2CSV.sheet_names` · *method*

## Summary:
Retrieves the names of all worksheets from an Excel file.

## Description:
This method opens an Excel file and extracts the names of all available worksheets. It handles both .xls (Excel 97-2003) and .xlsx (Excel 2007+) formats by using appropriate libraries (xlrd for .xls and openpyxl for .xlsx).

## Args:
    path (str): Filesystem path to the Excel file.
    filetype (str): File type identifier, either 'xls' or 'xlsx'.

## Returns:
    list[str]: A list of worksheet names contained in the Excel file.

## Raises:
    Exception: Propagates any exceptions raised during file operations or Excel parsing.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The path must point to a valid Excel file
    - The filetype must be either 'xls' or 'xlsx'
    - The Excel file must be readable
    
    Postconditions:
    - The input file handle is properly closed after processing
    - A list of sheet names is returned

## Side Effects:
    I/O: Reads from the filesystem at the specified path
    External service calls: Uses xlrd or openpyxl libraries for Excel parsing

### `csvkit.utilities.in2csv.In2CSV.main` · *method*

## Summary:
Converts input files of various formats (CSV, Excel, DBF, JSON, GeoJSON, fixed-width) to CSV format, handling special cases like sheet enumeration and multi-sheet Excel files.

## Description:
This method serves as the primary execution entry point for the in2csv utility, determining the input file format and processing it accordingly to produce CSV output. It handles automatic format detection, special flags like --names-only, and complex multi-sheet Excel file operations. The method orchestrates the conversion process by opening appropriate input files, applying necessary parsing parameters, and utilizing agate's table conversion capabilities.

## Args:
    self: The In2CSV instance containing command-line arguments and configuration

## Returns:
    None: This method performs I/O operations and does not return a value

## Raises:
    ValueError: When schema is required for fixed-width format but not provided, or when DBF files are attempted to be read from stdin
    SystemExit: When format detection fails or invalid combinations of arguments are provided (via argparser.error)

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
        - self.args.encoding
        - self.reader_kwargs
        - self.writer_kwargs
    Attributes WRITTEN:
        - self.input_file (opened and closed)
        - self.output_file (written to)

## Constraints:
    Preconditions:
        - Input file path must be specified when reading from stdin (not piped data)
        - Schema file must be provided when input format is fixed-width
        - DBF files cannot be processed from stdin (must be a filename)
        - Valid file format must be determinable or explicitly specified
    Postconditions:
        - Output is written to self.output_file in CSV format
        - Input file handle is properly closed
        - Schema file handle is properly closed when used

## Side Effects:
    - Reads from input file(s) based on detected or specified format
    - Writes to output file in CSV format
    - May read from additional files when --schema or --write-sheets is used
    - Opens and closes file handles for input and potentially multiple output files
    - May create additional CSV files when --write-sheets is used

## `csvkit.utilities.in2csv.launch_new_instance` · *function*

## Summary:
Creates and executes an In2CSV utility instance to convert input files to CSV format.

## Description:
This function serves as the primary entry point for launching the In2CSV utility, which converts various tabular data formats (CSV, Excel, DBF, JSON, GeoJSON, fixed-width) into standard CSV format. It instantiates the In2CSV class with default arguments and executes its run() method to process the input according to command-line options.

The function follows the standard csvkit utility pattern where a utility class is instantiated and its run() method is called to handle argument parsing, file operations, and main processing logic. This design allows for clean separation between instantiation and execution phases, enabling both command-line usage and programmatic invocation.

## Args:
    None

## Returns:
    None

## Raises:
    SystemExit: When argument validation fails or when the utility encounters fatal errors during execution
    UnicodeDecodeError: When input file encoding issues occur (handled by parent class)
    ValueError: When schema is required for fixed-width files but not provided, or when DBF files are read from stdin
    argparse.ArgumentTypeError: When invalid arguments are provided

## Constraints:
    Preconditions:
    - The function should be called in an environment where sys.argv is properly set up for argument parsing
    - Command-line arguments must be valid for the In2CSV utility
    - Input files must be accessible and readable when specified
    
    Postconditions:
    - The utility processes input according to specified options and writes output to stdout or specified output file
    - Input files are properly closed after processing
    - Standard csvkit error handling and logging mechanisms are applied

## Side Effects:
    - Reads from input files or stdin when specified
    - Writes to stdout or specified output file
    - May read from command-line arguments (sys.argv)
    - May raise SystemExit for error conditions

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[Create In2CSV instance]
    B --> C[Call utility.run()]
    C --> D{CSVKitUtility.run()}
    D --> E[Parses command-line arguments]
    E --> F[Opens input file if needed]
    F --> G[Calls utility.main()]
    G --> H{In2CSV.main()}
    H --> I[Determines input format]
    I --> J{Format type}
    J -->|Excel| K[Process Excel file]
    J -->|Other| L[Process other format]
    L --> M[Convert to CSV]
    K --> M
    M --> N[Write to output]
    N --> O[Close input file]
    O --> P[Return]
```

## Examples:
```python
# Typical usage from command line:
# in2csv input.xlsx > output.csv

# Programmatic usage:
from csvkit.utilities.in2csv import launch_new_instance

# This will process input according to command-line arguments
launch_new_instance()

# Alternative programmatic usage:
from csvkit.utilities.in2csv import In2CSV
utility = In2CSV()
utility.run()
```

