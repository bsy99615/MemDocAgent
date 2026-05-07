# `csvformat.py`

## `csvkit.utilities.csvformat.CSVFormat` · *class*

## Summary:
A command-line utility class for converting CSV files to custom output formats with configurable formatting options.

## Description:
The CSVFormat class is a command-line utility that converts CSV input into a customized output format with flexible formatting options. It extends CSVKitUtility to provide CSV-to-CSV conversion capabilities with extensive control over output delimiters, quoting styles, escape characters, and line terminators.

This class is designed to be instantiated and executed through the csvkit command-line framework when users invoke the csvformat utility. It provides a distinct abstraction for handling CSV output formatting operations, separating argument parsing, input processing, and output formatting concerns.

The class overrides the `_extract_csv_writer_kwargs` method from CSVKitUtility to customize writer parameters based on command-line arguments, allowing fine-grained control over the output CSV format.

## State:
- `description`: String describing the utility's purpose - 'Convert a CSV file to a custom output format.'
- `override_flags`: List of flags that are overridden from CSVKitUtility - ['L', 'blanks', 'date-format', 'datetime-format']
- `reader_kwargs`: Dictionary of keyword arguments for the input CSV reader, inherited from parent class via `_extract_csv_reader_kwargs()`
- `writer_kwargs`: Dictionary of keyword arguments for the output CSV writer, populated by `_extract_csv_writer_kwargs()` method
- `args`: Parsed command-line arguments from the argument parser

## Lifecycle:
- Creation: Automatically instantiated by the csvkit framework when executing the csvformat command
- Usage: Invoked through the standard CSVKitUtility.run() method which parses arguments and calls main()
- Destruction: Managed by Python's garbage collection; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[run()] --> B[main()]
    B --> C[_extract_csv_writer_kwargs]
    B --> D[skip_lines()]
    B --> E[additional_input_expected()]
    B --> F[agate.csv.reader]
    B --> G[agate.csv.writer]
    C --> H[writer_kwargs]
    D --> I[input_file]
    E --> J[sys.stdin]
    F --> K[reader]
    G --> L[writer]
    L --> M[writerows()]
```

## Raises:
- `ValueError`: When `skip_lines()` is called with a non-integer argument
- `UnicodeDecodeError`: When input file encoding doesn't match specified encoding
- `StopIteration`: When trying to read from empty input
- `argparse.ArgumentTypeError`: When invalid argument values are provided (inherited from parent class)

## Example:
```python
# Typical command-line usage:
# csvformat -D ',' -Q '"' -U 1 input.csv > output.csv

# Programmatic usage through csvkit framework:
from csvkit.utilities.csvformat import CSVFormat
utility = CSVFormat(['input.csv'])
utility.run()
```

### `csvkit.utilities.csvformat.CSVFormat.add_arguments` · *method*

## Summary:
Configures command-line arguments for output CSV formatting options including delimiter, quoting, and line termination settings.

## Description:
Adds command-line arguments to the argument parser for controlling the output format of CSV files. This method is part of the CSVFormat utility class and is called during initialization to set up all available output formatting options. The arguments defined here control how the output CSV file is written, including delimiters, quoting styles, and line terminators.

## Args:
    self: The CSVFormat instance whose argparser will be modified

## Returns:
    None: This method modifies the instance's argparser in-place and returns nothing

## Raises:
    None: This method does not raise exceptions directly

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies the argument parser instance)

## Constraints:
    Preconditions: 
    - The method must be called on a CSVFormat instance that has an argparser attribute
    - The argparser must be initialized (typically by CSVKitUtility._init_common_parser)
    
    Postconditions:
    - The instance's argparser contains all the output formatting arguments
    - Arguments are properly configured with appropriate help text and validation

## Side Effects:
    None: This method only modifies the internal argparser object and does not perform I/O operations or external service calls

### `csvkit.utilities.csvformat.CSVFormat._extract_csv_writer_kwargs` · *method*

## Summary:
Extracts CSV writer configuration parameters from command-line arguments for output formatting, extending base class functionality.

## Description:
This method processes command-line arguments to construct a dictionary of parameters suitable for configuring a CSV writer. It extends the base CSVKitUtility class's writer kwargs extraction by adding support for output-specific formatting options like delimiter, quoting, and line termination characters.

The method is invoked during CSVFormat initialization to prepare writer configuration parameters that will be passed to agate.csv.writer() when creating the output CSV file. This approach separates the concerns of argument parsing and writer configuration creation.

## Args:
    None

## Returns:
    dict: A dictionary containing CSV writer configuration parameters including:
        - 'line_numbers' (bool): Whether to include line numbers in output (when --linenumbers is specified)
        - 'delimiter' (str): Delimiter character for output CSV (tab when --out-tabs, custom when --out-delimiter)
        - 'quotechar' (str): Character used to quote strings in output
        - 'quoting' (int): Quoting style (0=Minimal, 1=All, 2=Non-numeric, 3=None)
        - 'doublequote' (bool): Whether to double quote in output
        - 'escapechar' (str): Character used to escape delimiters in output
        - 'lineterminator' (str): Character used to terminate lines in output

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
        - self.args.line_numbers
        - self.args.out_tabs
        - self.args.out_delimiter
        - self.args.out_quotechar
        - self.args.out_quoting
        - self.args.out_doublequote
        - self.args.out_escapechar
        - self.args.out_lineterminator

## Constraints:
    Preconditions:
        - self.args must be properly initialized with command-line arguments
        - The CSVFormat class must have added the appropriate output-related arguments (--out-* flags)
        
    Postconditions:
        - Returns a dictionary suitable for passing as keyword arguments to agate.csv.writer()
        - The returned dictionary may be empty if no output formatting options are specified
        - The 'delimiter' key is set to tab character when --out-tabs is specified, overriding --out-delimiter if both are present

## Side Effects:
    None

### `csvkit.utilities.csvformat.CSVFormat.main` · *method*

## Summary:
Processes and reformats CSV data according to command-line arguments, handling header rows, skipped lines, and output formatting.

## Description:
This method serves as the core processing routine for the CSVFormat utility. It reads CSV data from input (file or stdin), applies any specified transformations such as skipping initial lines or handling missing headers, and writes the processed data to the output file or stdout. The method orchestrates the CSV reading and writing process while respecting various command-line configuration options.

## Args:
    None - This is a method of a class instance, so it operates on the instance's attributes

## Returns:
    None - This method performs I/O operations and does not return a value

## Raises:
    None explicitly raised - Exceptions would be handled by the parent class mechanism

## State Changes:
    Attributes READ:
        - self.args: Command-line arguments parsed by the parent class
        - self.reader_kwargs: Keyword arguments for CSV reader construction
        - self.writer_kwargs: Keyword arguments for CSV writer construction
        - self.output_file: Output stream for writing results
    Attributes WRITTEN:
        - None - This method doesn't modify instance attributes directly

## Constraints:
    Preconditions:
        - Input file or stdin must be available for reading
        - Reader and writer keyword arguments must be properly configured
        - Command-line arguments must be parsed and available in self.args
    Postconditions:
        - All CSV data from input is written to output according to specified formatting rules
        - The output maintains proper CSV structure with appropriate headers and line handling

## Side Effects:
    - Writes to stdout/stderr when additional input is expected
    - Reads from stdin or input file
    - Writes to the output file or stdout
    - May cause stderr output when stdin is a TTY and no input is provided

## `csvkit.utilities.csvformat.launch_new_instance` · *function*

*No documentation generated.*

