# `csvsort.py`

## `csvkit.utilities.csvsort.CSVSort` · *class*

## Summary:
A command-line utility for sorting CSV files by specified columns, similar to the Unix "sort" command but designed for tabular data.

## Description:
The CSVSort class implements a command-line interface for sorting CSV data according to specified columns. It allows users to sort CSV files by one or more columns in ascending or descending order, with support for various CSV parsing options including delimiter detection, encoding specification, and type inference.

This class serves as a distinct abstraction for CSV sorting operations, encapsulating the logic for parsing command-line arguments, reading CSV data with appropriate type inference, identifying sort columns, performing the sort operation, and writing the sorted results back to output. It inherits from CSVKitUtility, which provides standard CSV processing capabilities like encoding handling, delimiter detection, and input/output management.

## State:
- `description` (str): Class-level description of the utility's purpose
- `argparser`: Argument parser instance configured with CSV processing options
- `args`: Parsed command-line arguments containing sort configuration
- `input_file`: Input file handle for reading CSV data
- `output_file`: Output file handle for writing sorted CSV data
- `reader_kwargs`: Keyword arguments for CSV reader configuration
- `writer_kwargs`: Keyword arguments for CSV writer configuration

The class maintains state through inherited CSVKitUtility attributes and follows the standard pattern of parsing arguments in `__init__` and processing data in `main()`.

## Lifecycle:
Creation: Instantiated automatically by the CSVKit framework when invoked from command line. Requires no explicit instantiation by user code.

Usage: The framework calls `run()` method which internally calls `main()`. The typical sequence is:
1. Parse command-line arguments via `add_arguments()` and `argparser.parse_args()`
2. Check for `--names` flag to display column information and exit
3. Validate that input is provided (file or stdin)
4. Parse column identifiers for sorting using `parse_column_identifiers()`
5. Read CSV data using `agate.Table.from_csv()` with appropriate settings
6. Sort data using `table.order_by()` with specified columns and direction
7. Write sorted data to output using `table.to_csv()`

Destruction: Managed by the CSVKit framework, which handles closing input files appropriately.

## Method Map:
```mermaid
graph TD
    A[CSVSort.run()] --> B[CSVSort.main()]
    B --> C{names_only flag?}
    C -->|Yes| D[print_column_names()]
    C -->|No| E[additional_input_expected()?]
    E -->|True| F[error: missing input]
    E -->|False| G[parse_column_identifiers()]
    G --> H[agate.Table.from_csv()]
    H --> I[table.order_by()]
    I --> J[table.to_csv()]
```

## Raises:
- `RequiredHeaderError`: When `--names` option is used with `--no-header-row`
- `argparse.ArgumentError`: When required input is missing (via `additional_input_expected`)
- `ValueError`: When invalid column ranges are specified (in `parse_column_identifiers`)
- Various exceptions from file I/O operations handled by the parent class
- `ColumnIdentifierError`: From `parse_column_identifiers` when column identifiers are invalid

## Example:
```bash
# Sort by first column in ascending order
csvsort input.csv > sorted.csv

# Sort by second column in descending order  
csvsort -c 2 -r input.csv > sorted.csv

# Sort by multiple columns (first and third)
csvsort -c 1,3 input.csv > sorted.csv

# Display column names and indices
csvsort -n input.csv

# Sort with custom delimiter
csvsort -d ';' -c 1 input.csv > sorted.csv

# Limit CSV dialect sniffing
csvsort -y 2048 -c 1 input.csv > sorted.csv
```

### `csvkit.utilities.csvsort.CSVSort.add_arguments` · *method*

## Summary:
Configures command-line arguments for the CSV sorting utility, defining options for sorting behavior and CSV parsing parameters.

## Description:
This method extends the base CSVKitUtility argument parser to include sorting-specific command-line options. It is called during the initialization phase of the CSVSort utility to register all available command-line flags and arguments that control how CSV files are sorted and parsed.

The method is part of the standard CSVKit utility pattern where each subclass implements its own add_arguments() method to define its specific command-line interface. This approach allows for consistent CLI behavior across all csvkit utilities while enabling each utility to define its unique functionality.

## Args:
    self: The CSVSort instance whose argparser will be configured

## Returns:
    None: This method modifies the instance's argparser in-place and returns nothing

## Raises:
    None: This method does not raise exceptions directly, though argument parsing may raise argparse-related exceptions

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies the argument parser instance)

## Constraints:
    Preconditions: 
    - The method must be called on a CSVSort instance that has an initialized argparser attribute
    - The parent CSVKitUtility.__init__ method must have been called to set up the basic argument parser
    
    Postconditions:
    - The instance's argparser contains all sorting-specific command-line arguments
    - All registered arguments will be available in self.args after parsing

## Side Effects:
    None: This method only configures the argument parser and does not perform I/O operations or modify external state

### `csvkit.utilities.csvsort.CSVSort.main` · *method*

## Summary:
Processes and sorts CSV data according to command-line arguments, writing the sorted result to output.

## Description:
This method serves as the primary execution entry point for the CSV sorting utility. It handles the complete workflow of reading CSV data, applying column-based sorting, and outputting the results. The method supports various CSV parsing options including delimiter specification, header handling, and column selection for sorting.

## Args:
    self: The CSVSort instance containing command-line arguments and configuration.

## Returns:
    None: This method performs I/O operations and does not return a value.

## Raises:
    SystemExit: When the --names-only flag is used (prints column names and exits) or when no input file is provided.

## State Changes:
    Attributes READ: 
    - self.args (command-line arguments)
    - self.input_file (input file handle)
    - self.output_file (output file handle)
    - self.reader_kwargs (CSV reader configuration)
    - self.writer_kwargs (CSV writer configuration)
    
    Attributes WRITTEN: 
    - None: This method doesn't modify instance attributes directly

## Constraints:
    Preconditions:
    - Command-line arguments must be properly parsed
    - Input file must be provided or piped data must be available via stdin
    - Column identifiers specified in --columns must be valid
    
    Postconditions:
    - CSV data is sorted according to specified columns
    - Sorted data is written to the output file or stdout

## Side Effects:
    - Reads from self.input_file (can be stdin or file)
    - Writes to self.output_file (can be stdout or file)
    - May raise SystemExit when validation fails
    - Uses agate.Table for CSV processing and sorting

## `csvkit.utilities.csvsort.launch_new_instance` · *function*

*No documentation generated.*

