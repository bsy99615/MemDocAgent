# `csvstack.py`

## `csvkit.utilities.csvstack._skip_lines` · *function*

*No documentation generated.*

## `csvkit.utilities.csvstack.CSVStack` · *class*

## Summary:
A command-line utility that stacks rows from multiple CSV files into a single output, optionally adding grouping information.

## Description:
The CSVStack utility combines rows from multiple CSV input files into a single output file by vertically concatenating them. It supports optional grouping columns that identify which source file each row originated from. This is useful for merging datasets that share the same schema but come from different sources.

The utility accepts multiple input files or piped stdin data and can handle various CSV formatting options through inherited CLI capabilities. It intelligently merges column headers from all input files and maintains proper row ordering.

## State:
- `description`: String describing the utility's purpose
- `override_flags`: List of flags that are overridden from the parent class
- `args`: Parsed command-line arguments from argparse
- `output_file`: File object for writing output (defaults to stdout)
- `reader_kwargs`: Dictionary of keyword arguments for CSV reader configuration
- `writer_kwargs`: Dictionary of keyword arguments for CSV writer configuration

## Lifecycle:
- Creation: Instantiated automatically by the CSVKit framework when invoked from command line
- Usage: Called via the `run()` method inherited from CSVKitUtility, which processes arguments and calls `main()`
- Destruction: Automatically closed by the parent class cleanup mechanisms

## Method Map:
```mermaid
graph TD
    A[CSVStack.run()] --> B[CSVStack.main()]
    B --> C[Parse input paths]
    B --> D[Process headers from all files]
    B --> E[Write header row to output]
    B --> F[Process each input file]
    F --> G[Read rows from file]
    F --> H[Add grouping info if needed]
    F --> I[Write rows to output]
    I --> J[Close file handle]
```

## Raises:
- `argparse.ArgumentTypeError`: When the number of grouping values doesn't match the number of input files
- `ValueError`: When skip_lines argument is not an integer
- `UnicodeDecodeError`: When input file encoding doesn't match specified encoding

## Example:
```bash
# Stack two CSV files with custom group names
csvstack -g "2020,2021" -n "year" file1.csv file2.csv

# Stack files using filenames as group values
csvstack --filenames file1.csv file2.csv

# Stack from stdin
cat file1.csv | csvstack -
```

### `csvkit.utilities.csvstack.CSVStack.add_arguments` · *method*

## Summary:
Sets up command-line interface options for stacking multiple CSV files with optional grouping.

## Description:
Configures the command-line argument parser for the CSVStack utility, enabling users to specify input CSV files and define grouping behavior when stacking multiple CSV files together. This method establishes the CLI interface that allows users to either pipe data through STDIN, specify one or more CSV files, and optionally add grouping columns to distinguish between the source files.

The method separates argument parsing logic from the core processing logic, improving modularity and maintainability. By defining these arguments upfront, the utility can properly handle various input scenarios including multiple files, STDIN input, and different grouping strategies (manual values or filename-based).

## Args:
    self: The CSVStack instance whose argparser will be configured

## Returns:
    None: This method modifies the instance's argparser in-place and returns nothing

## Raises:
    None: This method does not raise exceptions directly

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies the argument parser instance to add new arguments)

## Constraints:
    Preconditions: 
    - The method must be called on a CSVStack instance that has an argparser attribute
    - The argparser must be properly initialized before this method is called
    
    Postconditions:
    - The instance's argparser will contain the defined command-line arguments for:
      * FILE(s): one or more CSV files to stack (defaults to STDIN)
      * -g/--groups: comma-separated grouping values for each input file
      * -n/--group-name: custom name for the grouping column
      * --filenames: use filenames as grouping values instead of manual groups

## Side Effects:
    None: This method only modifies the internal argument parser configuration and has no external I/O or side effects

### `csvkit.utilities.csvstack.CSVStack.main` · *method*

## Summary:
Stacks multiple CSV files into a single output file, optionally adding group identifiers to distinguish source files.

## Description:
This method implements the core logic for the csvstack utility, which combines multiple CSV files into a single output stream. It handles various input scenarios including stdin, multiple files, and grouped output. The method processes each input file sequentially, reads its content according to specified CSV parameters, and writes the combined result to the output file.

## Args:
    self: The CSVStack instance containing configuration and state

## Returns:
    None: This method performs I/O operations and does not return a value

## Raises:
    SystemExit: When the number of grouping values doesn't match the number of input files
    ValueError: When skip_lines argument is not an integer

## State Changes:
    Attributes READ: 
    - self.args.input_paths
    - self.args.groups
    - self.args.group_by_filenames
    - self.args.group_name
    - self.args.no_header_row
    - self.args.skip_lines
    - self.output_file
    - self.reader_kwargs
    - self.writer_kwargs
    - self.argparser
    
    Attributes WRITTEN: 
    - None: This method doesn't modify instance attributes directly

## Constraints:
    Preconditions:
    - Input paths must be valid or stdin must be available for reading
    - If groups are specified, the number of group values must equal the number of input files
    - CSV reader/writer parameters must be properly configured
    
    Postconditions:
    - Output file contains stacked CSV data from all input files
    - If grouping is enabled, a group column is added to identify source files
    - Header row is written if appropriate based on configuration

## Side Effects:
    - Reads from multiple input files or stdin
    - Writes to the output file
    - Writes informational messages to stderr when stdin is expected
    - May close file handles after processing

## `csvkit.utilities.csvstack.launch_new_instance` · *function*

*No documentation generated.*

