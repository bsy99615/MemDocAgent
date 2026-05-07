# `csvcut.py`

## `csvkit.utilities.csvcut.CSVCut` · *class*

*No documentation generated.*

### `csvkit.utilities.csvcut.CSVCut.add_arguments` · *method*

*No documentation generated.*

### `csvkit.utilities.csvcut.CSVCut.main` · *method*

## Summary:
Processes CSV data by selecting specific columns and writing them to output, with optional column name display or empty row filtering.

## Description:
This method implements the core logic for the csvcut utility, which allows users to select specific columns from CSV files. When the --names-only flag is specified, it displays column names instead of processing data. Otherwise, it reads CSV rows, selects specified columns, and writes them to the output file. The method supports various CSV parsing options through inherited configuration and can filter out empty rows when the --delete-empty flag is used.

The method follows a specific execution flow:
1. If --names-only flag is set, prints column names and returns early
2. If no input is provided and stdin is a terminal, displays a waiting message
3. Processes input to extract rows, column names, and column IDs
4. Writes header row with selected column names
5. Processes each data row, selecting specified columns and optionally filtering empty rows

## Args:
    None - This is a method that operates on self and uses instance variables

## Returns:
    None - This method performs I/O operations and does not return a value

## Raises:
    RequiredHeaderError - When --names-only is used with --no-header-row flag
    ColumnIdentifierError - When invalid column identifiers are provided in the --columns argument

## State Changes:
    Attributes READ: self.args, self.output_file, self.reader_kwargs, self.writer_kwargs
    Attributes WRITTEN: None - This method doesn't modify instance state directly

## Constraints:
    Preconditions: 
    - The CSV input must be properly configured through the parent class initialization
    - If --names-only is used, --no-header-row must not be set
    - Column identifiers in --columns must be valid for the input CSV structure
    
    Postconditions:
    - Output file contains processed CSV data with selected columns
    - Column names are displayed when --names-only flag is used
    - Empty rows are filtered when --delete-empty flag is used

## Side Effects:
    - Writes to self.output_file (stdout by default)
    - Writes to stderr when waiting for stdin input
    - Reads from stdin when no input file is provided and no piped data exists
    - Uses agate.csv.writer for CSV output formatting

## `csvkit.utilities.csvcut.launch_new_instance` · *function*

*No documentation generated.*

