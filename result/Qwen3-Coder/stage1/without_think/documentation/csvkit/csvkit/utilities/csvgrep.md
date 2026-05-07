# `csvgrep.py`

## `csvkit.utilities.csvgrep.CSVGrep` · *class*

## Summary:
A command-line utility for searching CSV files using string matching, regular expressions, or file-based lookups, similar to the Unix grep command but adapted for tabular data.

## Description:
The CSVGrep class implements a CSV file filtering utility that allows users to search for specific patterns within CSV data. It supports multiple search modes including literal string matching, regular expression matching, and file-based matching where each line in a file is treated as a potential match. The utility can filter rows based on whether all columns match the pattern or any column matches, and can invert the matching logic to select non-matching rows.

This class is designed to be used as a standalone command-line tool and integrates with the csvkit framework for CSV processing. It inherits from CSVKitUtility, providing standard CSV handling capabilities such as encoding support, delimiter detection, and header row management.

The utility processes command-line arguments to configure filtering behavior, then applies the selected pattern matching strategy across specified columns. It leverages the FilteringCSVReader class for efficient row filtering and agate for CSV output formatting.

## State:
- `description` (str): Class-level description of the utility's purpose - "Search CSV files. Like the Unix \"grep\" command, but for tabular data."
- `override_flags` (list[str]): Flags that are overridden from the parent CSVKitUtility class - ['L', 'blanks', 'date-format', 'datetime-format']
- `argparser`: Argument parser instance configured with command-line options for various filtering modes
- `args`: Parsed command-line arguments containing user specifications for search patterns and filtering options
- `output_file`: Output file handle for writing filtered results (defaults to stdout)
- `reader_kwargs`: Keyword arguments for CSV reader configuration (includes delimiter, quoting, etc.)
- `writer_kwargs`: Keyword arguments for CSV writer configuration (includes line numbers, etc.)

## Lifecycle:
- Creation: Instantiated by the csvkit command-line framework when invoked via CLI
- Usage: Called via the `run()` method inherited from CSVKitUtility, which internally calls `main()`. The main method processes arguments, reads input CSV data, applies filtering logic, and writes results
- Destruction: Automatically handled by the parent class lifecycle management, including proper file closing

## Method Map:
```mermaid
graph TD
    A[CSVGrep.run()] --> B[CSVGrep.main()]
    B --> C[CSVGrep.get_rows_and_column_names_and_column_ids()]
    C --> D[parse_column_identifiers()]
    B --> E[FilteringCSVReader.__init__()]
    E --> F[standardize_patterns()]
    F --> G[Pattern matching functions]
    E --> H[FilteringCSVReader.test_row()]
    H --> I[Row filtering logic]
    B --> J[agate.csv.writer()]
    J --> K[Output rows]
```

## Raises:
- `argparse.ArgumentError`: When required arguments are missing (e.g., no columns specified, no search pattern provided)
- `ColumnIdentifierError`: When column identifiers in the -c option are invalid or ambiguous
- `UnicodeDecodeError`: When input file encoding is incorrect (handled by parent class)
- `FileNotFoundError`: When specified input file or match file doesn't exist
- `ValueError`: When invalid column ranges or numeric identifiers are provided

## Example:
```bash
# Search for "John" in the name column of data.csv
python csvgrep.py -c name -m John data.csv

# Search for phone numbers using regex in the phone column
python csvgrep.py -c phone -r "^\d{3}-\d{3}-\d{4}$" data.csv

# Display column names and indices
python csvgrep.py -n data.csv

# Search for values in a lookup file
python csvgrep.py -c email -f lookup.txt data.csv

# Invert match to find non-matching rows
python csvgrep.py -c name -m John -i data.csv

# Match any column instead of all columns
python csvgrep.py -c name,email -m John -a data.csv
```

### `csvkit.utilities.csvgrep.CSVGrep.add_arguments` · *method*

## Summary:
Configures command-line arguments for the CSV grep utility to filter rows based on text matching criteria.

## Description:
Adds command-line argument definitions to the utility's argument parser for filtering CSV data. This method sets up options for specifying which columns to search, the search pattern (literal string, regex, or file-based), and filtering behavior (invert match, any column match).

## Args:
    self: The CSVGrep utility instance containing the argument parser to configure.

## Returns:
    None: This method modifies the instance's argument parser in-place and returns nothing.

## Raises:
    None: This method does not raise exceptions directly.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies the argument parser instance)

## Constraints:
    Preconditions: The method assumes self.argparser exists and is an argparse.ArgumentParser instance.
    Postconditions: The argument parser is configured with all csvgrep-specific command-line options.

## Side Effects:
    None: This method only configures the argument parser and doesn't perform I/O or mutate external state.

### `csvkit.utilities.csvgrep.CSVGrep.main` · *method*

## Summary:
Filters CSV rows based on pattern matching in specified columns, writing matching rows to output.

## Description:
This method implements the core CSV grep functionality by reading CSV data, applying pattern filters to specified columns, and outputting rows that match the criteria. It supports multiple pattern specification methods including literal strings, regular expressions, and file-based pattern matching. The method handles various command-line arguments for controlling filtering behavior such as inverse matching, any-match logic, and column selection.

## Args:
    self: The CSVGrep instance containing command-line arguments and configuration

## Returns:
    None

## Raises:
    SystemExit: When command-line argument validation fails (missing required arguments or invalid combinations)

## State Changes:
    Attributes READ:
        - self.args.names_only
        - self.args.columns
        - self.args.regex
        - self.args.pattern
        - self.args.matchfile
        - self.args.inverse
        - self.args.any_match
        - self.reader_kwargs
        - self.writer_kwargs
    Attributes WRITTEN:
        - self.output_file (via write operations)
        - self.args.matchfile (closed when used)

## Constraints:
    Preconditions:
        - Command-line arguments must be parsed and available in self.args
        - At least one column must be specified with -c option
        - One of -r, -m, or -f options must be specified (unless using -n)
        - Input file must be readable or stdin must be available for piped data
        - CSV data must be properly formatted with valid column structure
    Postconditions:
        - Matching rows are written to self.output_file
        - Column names are written as header row to output
        - If -n option is used, column names are printed instead of filtered rows

## Side Effects:
    - Reads from input file or stdin
    - Writes filtered CSV data to self.output_file (stdout by default)
    - May write informational message to stderr when waiting for stdin input
    - Closes self.args.matchfile when used
    - Uses agate.csv.writer for output formatting
    - Uses re.compile for regex pattern compilation

## `csvkit.utilities.csvgrep.launch_new_instance` · *function*

## Summary:
Creates and executes a new CSVGrep utility instance for filtering CSV data based on search patterns.

## Description:
This function serves as the entry point for launching the CSVGrep command-line utility. It instantiates a CSVGrep object and invokes its run method to process command-line arguments and filter CSV data according to specified search criteria. The function follows the standard csvkit utility pattern where each command-line tool provides a launch_new_instance function that handles instantiation and execution.

The CSVGrep utility supports multiple search modes including literal string matching, regular expression matching, and file-based matching. It can filter rows based on whether all columns match the pattern or any column matches, and supports inverting the matching logic to select non-matching rows.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised by this function, though the underlying CSVGrep.run() method may raise:
    - argparse.ArgumentError: When required arguments are missing (e.g., no columns specified, no search pattern provided)
    - ColumnIdentifierError: When column identifiers in the -c option are invalid or ambiguous
    - UnicodeDecodeError: When input file encoding is incorrect (handled by parent class)
    - FileNotFoundError: When specified input file or match file doesn't exist
    - ValueError: When invalid column ranges or numeric identifiers are provided

## Constraints:
    Precondition: The function assumes that command-line arguments are available via sys.argv or have been properly set up in the calling context.
    Postcondition: The function completes execution by running the CSVGrep utility, which may produce output to stdout or write to a file.

## Side Effects:
    - Reads from stdin or specified input file(s) for CSV data processing
    - Writes filtered CSV results to stdout or specified output file
    - May read from external files when using file-based matching (-f option)
    - Processes command-line arguments from sys.argv

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[CSVGrep().__init__()]
    B --> C[utility.run()]
    C --> D[CSVKitUtility.run()]
    D --> E[Parse command-line args]
    E --> F[Open input file]
    F --> G[Call CSVGrep.main()]
    G --> H[Process filtering logic]
    H --> I[Write results to output]
    I --> J[Return]
```

## Examples:
```bash
# Basic usage - search for "John" in the name column
python csvgrep.py -c name -m John data.csv

# Regular expression search for phone numbers
python csvgrep.py -c phone -r "^\d{3}-\d{3}-\d{4}$" data.csv

# File-based lookup search
python csvgrep.py -c email -f lookup.txt data.csv

# Invert match to find non-matching rows
python csvgrep.py -c name -m John -i data.csv
```

