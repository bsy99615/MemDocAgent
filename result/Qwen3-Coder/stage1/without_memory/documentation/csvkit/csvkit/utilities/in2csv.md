# `in2csv.py`

## `csvkit.utilities.in2csv.In2CSV` · *class*

*No documentation generated.*

### `csvkit.utilities.in2csv.In2CSV.add_arguments` · *method*

## Summary:
Configures command-line arguments for the in2csv utility to support conversion of various tabular data formats to CSV.

## Description:
This method configures the argument parser with all available command-line options for converting different tabular data formats to CSV. It defines positional and optional arguments that control input file handling, format specification, special conversion parameters for different file types (Excel, fixed-width, JSON), and various processing options such as CSV dialect sniffing and type inference. The method establishes the complete CLI interface for the in2csv utility, enabling users to specify input files, conversion formats, and processing parameters.

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
    - The SUPPORTED_FORMATS constant must be defined in the module scope and contain valid format identifiers
    
    Postconditions:
    - self.argparser will contain all the defined command-line arguments for in2csv functionality
    - All argument configurations are properly set up for CLI parsing and validation

## Side Effects:
    None: This method only configures the argument parser and doesn't perform I/O operations or modify external state

## Detailed Argument List:
- FILE (positional): The CSV file to operate on. If omitted, will accept input as piped data via STDIN.
- -f, --format: Specify the format of the input file. If not specified, will be inferred from the file type. Choices are determined by SUPPORTED_FORMATS.
- -s, --schema: Specify a CSV-formatted schema file for converting fixed-width files.
- -k, --key: Specify a top-level key to look within for a list of objects to be converted when processing JSON.
- -n, --names: Display sheet names from the input Excel file.
- --sheet: Specify the name of the Excel sheet to operate on.
- --write-sheets: Specify the names of Excel sheets to write to files, or "-" to write all sheets.
- --use-sheet-names: Use the sheet names as file names when --write-sheets is set.
- --encoding-xls: Specify the encoding of the input XLS file.
- -y, --snifflimit: Limit CSV dialect sniffing to the specified number of bytes. Specify "0" to disable sniffing entirely, or "-1" to sniff the entire file.
- -I, --no-inference: Disable type inference (and --locale, --date-format, --datetime-format) when parsing CSV input.

### `csvkit.utilities.in2csv.In2CSV.open_excel_input_file` · *method*

*No documentation generated.*

### `csvkit.utilities.in2csv.In2CSV.sheet_names` · *method*

## Summary:
Retrieves the names of all sheets from an Excel workbook file.

## Description:
This method opens an Excel file and extracts the names of all available sheets. It supports both .xls (Excel 97-2003) and .xlsx (Excel 2007+) formats by using appropriate libraries (xlrd for .xls and openpyxl for .xlsx). This method is primarily used when the user requests to display sheet names (--names flag) or when writing multiple sheets to separate files (--write-sheets flag with '-' value).

## Args:
    path (str): Path to the Excel file, or None/empty string for stdin input
    filetype (str): File type identifier, either 'xls' or 'xlsx'

## Returns:
    list[str]: A list of sheet names contained in the Excel workbook

## Raises:
    None explicitly raised, but underlying library calls may raise exceptions such as:
    - xlrd.XLRDError for invalid .xls files
    - openpyxl.utils.exceptions.InvalidFileException for invalid .xlsx files
    - IOError for file access issues

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - The path argument must be a valid path to an Excel file or None/stdin
    - The filetype argument must be either 'xls' or 'xlsx'
    - The file at path must be readable and contain valid Excel data
    
    Postconditions:
    - The input file handle is closed after reading
    - Returns a list of sheet names (possibly empty)

## Side Effects:
    - Opens and closes a file handle to read Excel data
    - Reads entire Excel file contents into memory temporarily
    - May perform I/O operations to access the file system

### `csvkit.utilities.in2csv.In2CSV.main` · *method*

## Summary:
Converts input files of various formats (CSV, Excel, JSON, DBF, etc.) to CSV format, with support for various command-line options and special processing modes.

## Description:
This method serves as the primary entry point for the in2csv utility, orchestrating the conversion of input files from their native formats to CSV format. It determines the input file type, handles special modes like schema inspection (-n/--names-only), processes the input according to format-specific logic, and writes the resulting CSV data to the output stream. The method supports multiple input formats including CSV, Excel spreadsheets (XLS/XLSX), DBF databases, JSON, GeoJSON, and fixed-width files.

## Args:
    self: The In2CSV instance containing command-line arguments and configuration

## Returns:
    None: This method performs I/O operations and does not return a value

## Raises:
    ValueError: When schema is required for fixed-format files but not provided, or when DBF files are attempted to be read from stdin
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
        - self.input_file (set to opened input file handle)
        - self.output_file (used for writing CSV output)

## Constraints:
    Preconditions:
        - Input file path must be specified when not reading from stdin
        - Schema file must be provided when converting fixed-width files
        - DBF files cannot be processed from stdin (must be a filename)
        - When using -n/--names-only, input must be Excel file (.xls or .xlsx)
    Postconditions:
        - Input file is properly closed after processing
        - Output CSV data is written to self.output_file
        - If write_sheets option is used, individual CSV files are created for each Excel sheet

## Side Effects:
    - Opens and closes input file handles
    - Opens and closes schema file handle (when applicable)
    - Writes to stdout/stderr (via self.output_file)
    - Creates new files on disk (when write_sheets option is used)
    - May perform I/O operations on the filesystem for temporary file handling

## `csvkit.utilities.in2csv.launch_new_instance` · *function*

*No documentation generated.*

