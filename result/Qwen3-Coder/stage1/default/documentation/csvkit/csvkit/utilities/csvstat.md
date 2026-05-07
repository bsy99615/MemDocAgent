# `csvstat.py`

## `csvkit.utilities.csvstat.CSVStat` · *class*

## Summary:
CSVStat is a command-line utility for computing descriptive statistics of CSV file columns.

## Description:
CSVStat is a command-line utility that processes CSV files to compute and display descriptive statistics for specified columns. It inherits from CSVKitUtility and adds functionality for statistical analysis including counts, sums, means, medians, standard deviations, min/max values, and frequency distributions. The utility supports multiple output formats (plain text, CSV, JSON) and allows selective column and operation specification.

This utility is designed for data exploration and quality assessment, providing automated statistical summaries of CSV datasets through command-line interface.

## State:
- argparser (argparse.ArgumentParser): Configured argument parser with common CSV options and CSVStat-specific arguments
- args (argparse.Namespace): Parsed command-line arguments containing all user-specified options
- output_file (file-like object): Output destination for results (defaults to stdout)
- input_file (file-like object): Input file handle for CSV data processing
- reader_kwargs (dict): Keyword arguments for CSV reader construction
- writer_kwargs (dict): Keyword arguments for CSV writer construction

## Lifecycle:
- Creation: Instantiated with command-line arguments, initializes argument parser and sets up CSV processing infrastructure
- Usage: Called via run() method which parses arguments, opens input file, and executes main() method for processing
- Destruction: Automatic cleanup of file handles through parent class mechanisms

## Method Map:
```mermaid
graph TD
    A[CSVStat.run] --> B[CSVStat.add_arguments]
    B --> C[CSVStat.main]
    C --> D{names_only?}
    D -- Yes --> E[CSVStat.print_column_names]
    D -- No --> F{count_only?}
    F -- Yes --> G[CSVStat.count calculation]
    F -- No --> H[CSVStat.parse_column_identifiers]
    H --> I{operations specified?}
    I -- Yes --> J[CSVStat.print_one]
    I -- No --> K[CSVStat.calculate_stats]
    K --> L{output format}
    L --> M[CSVStat.print_csv|print_json|print_stats]
```

## Raises:
- SystemExit: Raised by argparser.error() when invalid argument combinations are detected
- ValueError: Raised by skip_lines() when skip_lines argument is not an integer
- RequiredHeaderError: Raised by print_column_names() when --no-header-row is used with -n/--names options
- UnicodeDecodeError: Handled by custom exception handler for encoding issues

## Example:
```python
# Basic usage to get all statistics for all columns
# python csvstat.py data.csv

# Get only mean and median for specific columns
# python csvstat.py -c 1,3 --mean --median data.csv

# Output as CSV format
# python csvstat.py --csv data.csv

# Display only column names and indices
# python csvstat.py -n data.csv

# Get row count only
# python csvstat.py --count data.csv
```

### `csvkit.utilities.csvstat.CSVStat.add_arguments` · *method*

## Summary:
Configures command-line argument parsers for the CSVStat utility, defining all available options for statistical analysis of CSV columns.

## Description:
This method extends the base CSVKitUtility argument parser with specialized options for the csvstat command-line tool. It adds arguments for controlling output format (CSV, JSON, plain text), selecting specific columns for analysis, choosing specific statistical operations to perform, and configuring various CSV processing behaviors. The method is called during the initialization phase of CSVKitUtility to set up all available command-line options before parsing user input.

This logic is separated into its own method to follow the inheritance pattern established by CSVKitUtility, allowing subclasses to customize argument parsing while maintaining consistent base functionality. It enables the csvstat utility to support a wide variety of statistical analysis options through command-line flags.

## Args:
    None - This is a method of the CSVStat class and takes no explicit arguments beyond 'self'

## Returns:
    None - This method modifies the instance's argument parser in-place and returns nothing

## Raises:
    None - This method does not raise exceptions directly, though argument parsing may raise argparse errors

## State Changes:
    Attributes READ: 
    - self.argparser (argparse.ArgumentParser instance used for command-line argument parsing)

    Attributes WRITTEN:
    - self.argparser (modified with new argument definitions)

## Constraints:
    Preconditions:
    - The method must be called after CSVKitUtility initialization but before argument parsing
    - The self.argparser attribute must be initialized (inherited from CSVKitUtility)

    Postconditions:
    - All command-line arguments defined in this method are registered with the argument parser
    - The argument parser is ready to process user input for csvstat operations

## Side Effects:
    None - This method only registers arguments with the argument parser and does not perform I/O or external service calls

### `csvkit.utilities.csvstat.CSVStat.main` · *method*

## Summary:
Main execution method for the CSVStat command-line utility that processes CSV files and generates statistical analysis or metadata reports.

## Description:
This method serves as the primary entry point for the csvstat utility, orchestrating the entire workflow for analyzing CSV data. It handles various command-line arguments to determine the type of analysis to perform, validates input requirements, parses column specifications, and delegates to appropriate output methods based on user preferences.

The method implements a decision tree that routes execution to different code paths depending on flags like --names-only, --count-only, --csv, --json, or specific statistical operations (--mean, --median, etc.). It also performs input validation and error checking for conflicting arguments.

## Args:
    self: Instance of CSVStat class containing parsed command-line arguments and utility methods

## Returns:
    None: This method performs I/O operations and does not return a value

## Raises:
    SystemExit: Raised by argparser.error() when validation fails for conflicting arguments or missing input

## State Changes:
    Attributes READ:
        - self.args: Command-line arguments namespace containing all parsed options
        - self.input_file: Input file handle for reading CSV data
        - self.output_file: Output file handle for writing results
        - self.reader_kwargs: Keyword arguments for CSV reader construction
    
    Attributes WRITTEN:
        - None: This method doesn't modify instance attributes directly

## Constraints:
    Preconditions:
        - Command-line arguments must be properly parsed before calling
        - Input file must be readable or piped data must be available
        - When using column-specific operations, valid column identifiers must be provided
        - Only one statistical operation flag may be specified at a time
    
    Postconditions:
        - Output is written to self.output_file according to selected format
        - Appropriate error messages are displayed for invalid configurations

## Side Effects:
    - Reads from self.input_file (CSV input)
    - Writes to self.output_file (analysis results)
    - May read from stdin if no input file is provided
    - Calls various helper methods that may perform additional I/O operations
    - May raise SystemExit for argument validation errors

## Execution Paths:
    1. Names-only mode: If --names-only flag is set, prints column names and exits
    2. Input validation: Checks for required input file or piped data
    3. Operation conflict validation: Ensures only one statistical operation is specified
    4. Count-only mode: If --count-only flag is set, counts rows and writes count to output
    5. Full analysis mode: For normal operation, reads CSV data into agate Table, parses column identifiers, and either:
       - Performs single operation on specified columns (via print_one)
       - Calculates statistics for all specified columns (via calculate_stats) and outputs in requested format (CSV, JSON, or human-readable)

### `csvkit.utilities.csvstat.CSVStat.is_finite_decimal` · *method*

*No documentation generated.*

### `csvkit.utilities.csvstat.CSVStat._calculate_stat` · *method*

## Summary:
Calculates statistical values for a given column in a CSV table using either custom getter functions or aggregation operations.

## Description:
This private method serves as the core calculation engine for statistical operations in the CSVStat utility. It determines whether to use a specialized getter function (for operations like frequency counts) or fall back to standard aggregation operations defined in the OPERATIONS configuration. The method handles proper formatting of decimal values and error handling for invalid operations.

The method is called by `print_one` and `calculate_stats` methods during the statistical analysis process. It's separated from inline logic to provide a clean abstraction for statistical computation while handling various edge cases like formatting and error recovery.

## Args:
    table (agate.Table): The table containing the data to analyze
    column_id (int): Index of the column to calculate statistics for
    op_name (str): Name of the operation being performed (e.g., 'mean', 'sum', 'freq')
    op_data (dict): Configuration data for the operation including 'aggregation' key
    **kwargs: Additional keyword arguments that may be passed to getter functions

## Returns:
    Various: The calculated statistic value, potentially formatted as a string for display purposes

## Raises:
    None explicitly raised - uses a bare except clause that silently ignores errors

## State Changes:
    Attributes READ: 
    - self.args.json_output
    - self.args.decimal_format
    - self.args.no_grouping_separator
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - table must be a valid agate.Table instance
    - column_id must be a valid index for the table's columns
    - op_name must correspond to a valid operation in OPERATIONS
    - op_data must contain an 'aggregation' key for non-getter operations
    
    Postconditions:
    - Returns a calculated statistic value or None if operation fails
    - For finite decimal values, returns properly formatted string when not in JSON mode
    - Error conditions are silently handled and return None

## Side Effects:
    - Uses warnings.catch_warnings() to suppress agate.NullCalculationWarning
    - May perform locale-aware decimal formatting via format_decimal function
    - Makes calls to agate Table.aggregate() method
    - Silently ignores all exceptions during calculation

### `csvkit.utilities.csvstat.CSVStat.calculate_stats` · *method*

## Summary:
Computes all registered statistical operations for a specified column and returns results as a dictionary.

## Description:
This method serves as the core statistical computation engine for the CSVStat utility. It iterates through all predefined statistical operations defined in the OPERATIONS class constant and calculates each statistic for the specified column using the private `_calculate_stat` method. The results are aggregated into a dictionary where keys are operation names and values are the computed statistical measures.

This method is typically invoked during the column statistics generation phase of CSV analysis, providing a complete statistical profile for a given column. It enables the CSVStat utility to deliver comprehensive descriptive statistics without requiring manual iteration over individual operations.

## Args:
    table (agate.Table): The table containing the data to analyze
    column_id (int or str): Identifier for the column to analyze (column index or name)
    **kwargs: Additional keyword arguments passed through to individual calculation methods

## Returns:
    dict: Dictionary mapping operation names (str) to computed statistical values (type varies by operation)

## Raises:
    Exception: May raise exceptions from underlying `_calculate_stat` method implementations
    KeyError: If column_id does not correspond to a valid column in table
    TypeError: If table is not a valid agate.Table instance

## State Changes:
    Attributes READ: OPERATIONS constant (class attribute)
    Attributes WRITTEN: None (method is read-only)

## Constraints:
    Preconditions:
    - table parameter must be a valid agate.Table instance
    - column_id must reference a valid column in the table
    - OPERATIONS constant must be defined at class level
    - _calculate_stat method must be implemented in the class
    - All operations in OPERATIONS must be valid operation identifiers

    Postconditions:
    - Returns a dictionary containing results for all operations in OPERATIONS
    - Each returned value corresponds to the result of applying the respective operation to the specified column

## Side Effects:
    None - Pure computational method with no external I/O or state mutation

### `csvkit.utilities.csvstat.CSVStat.print_stats` · *method*

## Summary:
Prints formatted statistical information for specified columns in a CSV table to the output file.

## Description:
This method generates human-readable statistical summaries for each specified column in a CSV table. It formats and displays various statistical measures including counts, frequencies, min/max values, sums, means, medians, standard deviations, and other descriptive statistics. The output follows a consistent format with column headers, labeled statistics, and proper alignment for readability.

The method is called by the main execution flow when no specific operation flags are provided and the output format is plain text. It processes all columns in the provided column_ids list and displays their statistics in a structured, aligned format suitable for console output.

## Args:
    table (agate.Table): The CSV table containing the data to analyze
    column_ids (list[int]): List of column indices to generate statistics for
    stats (dict): Dictionary mapping column indices to their computed statistics

## Returns:
    None: This method performs I/O operations and does not return a value

## Raises:
    None explicitly raised: The method relies on underlying I/O operations and assumes valid inputs

## State Changes:
    Attributes READ:
    - self.output_file: File handle for writing formatted output
    - self.args.decimal_format: Format string for decimal number formatting
    - self.args.no_grouping_separator: Flag controlling thousands separator usage
    
    Attributes WRITTEN:
    - self.output_file: Writes formatted statistical output to the file handle

## Constraints:
    Preconditions:
    - table must be a valid agate.Table instance
    - column_ids must contain valid column indices for the table
    - stats dictionary must contain computed statistics for all specified columns
    - OPERATIONS constant must be defined at class level with operation definitions
    - self.output_file must be a valid file handle for writing
    
    Postconditions:
    - Statistics for all specified columns are written to self.output_file
    - Output follows a consistent format with proper alignment and labeling
    - Row count summary is appended at the end of output

## Side Effects:
    I/O: Writes formatted statistical information to self.output_file
    File Operations: Writes to the output file handle (typically stdout)

### `csvkit.utilities.csvstat.CSVStat.print_csv` · *method*

*No documentation generated.*

### `csvkit.utilities.csvstat.CSVStat.print_json` · *method*

## Summary:
Converts CSV column statistics to JSON format and writes them to the output file.

## Description:
This method transforms column statistics data into a JSON array format, where each element represents a column with its ID, name, and calculated statistics. It is called when the user specifies the --json flag to output statistics in JSON format instead of plain text or CSV.

## Args:
    table: agate.Table - The CSV data table containing the columns to analyze
    column_ids: list[int] - List of column indices to include in the statistics
    stats: dict - Dictionary mapping column IDs to their calculated statistics

## Returns:
    None - This method doesn't return a value but writes directly to self.output_file

## Raises:
    None explicitly raised - However, underlying json.dump() may raise JSON-related exceptions

## State Changes:
    Attributes READ: self.output_file, self.args.indent
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - table must be a valid agate.Table instance
    - column_ids must be a list of valid column indices
    - stats must be a properly formatted dictionary with column statistics
    - self.output_file must be opened for writing
    - self.args.indent must be either None or an integer

    Postconditions:
    - Data is written to self.output_file in JSON format
    - The JSON output contains an array of objects, each representing a column with its statistics

## Side Effects:
    - Writes JSON-formatted data to self.output_file
    - Uses json.dump() which may perform I/O operations
    - May format decimal numbers using default_float_decimal for proper JSON serialization

### `csvkit.utilities.csvstat.CSVStat._rows` · *method*

## Summary:
Generates formatted output rows containing column statistics for CSV analysis.

## Description:
This method transforms statistical data for CSV columns into a standardized row format suitable for CSV or JSON output. It's designed to be used by the `print_csv` and `print_json` methods to format column statistics for structured output.

The method iterates through specified column IDs, retrieves column names and statistics, and creates output rows that include column metadata and computed statistics. It filters out None values to avoid including undefined statistics in the output.

Known callers:
- `print_csv()` - Uses this method to generate rows for CSV output
- `print_json()` - Uses this method to generate rows for JSON output

This method exists to centralize the formatting logic for column statistics, avoiding duplication between CSV and JSON output formats.

## Args:
    table (agate.Table): The CSV table containing the data being analyzed
    column_ids (list[int]): List of column indices to process
    stats (dict): Dictionary mapping column indices to their computed statistics

## Returns:
    generator: Yields dictionaries representing formatted rows with column_id, column_name, and applicable statistics

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - table.column_names
    - stats[column_id] for each column_id
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - table must be a valid agate.Table instance
    - column_ids must be valid indices for table.column_names
    - stats must be a dictionary with column_id keys mapping to statistic dictionaries
    - Each column_id in column_ids must exist in stats dictionary
    - The global variable OPERATIONS must be defined with statistical operation definitions
    
    Postconditions:
    - Each yielded dictionary contains 'column_id' and 'column_name' keys
    - Statistics included in the output are those that are not None
    - Output rows are formatted consistently for CSV/JSON serialization

## Side Effects:
    None

## `csvkit.utilities.csvstat.format_decimal` · *function*

## Summary:
Formats a decimal number using locale-aware formatting with customizable precision and grouping separators.

## Description:
This utility function applies locale-specific formatting to decimal numbers, allowing for customizable precision and optional grouping separators. It's designed to provide consistent, localized numeric formatting for display purposes in CSV statistics output. The function removes trailing zeros from the formatted result to provide cleaner presentation.

The function extracts formatting logic into a separate utility to promote code reuse and maintainability, separating concerns between data processing and presentation formatting.

## Args:
    d (float or Decimal): The decimal number to format
    f (str, optional): Format string specifying precision. Defaults to '%.3f' (3 decimal places)
    no_grouping_separator (bool, optional): When True, disables thousands separators. Defaults to False

## Returns:
    str: Formatted string representation of the decimal number with trailing zeros removed.
         Returns empty string for edge cases where stripping results in just "." character.

## Raises:
    TypeError: If 'd' is not a numeric type
    ValueError: If 'f' is not a valid format string

## Constraints:
    Preconditions:
    - Input 'd' must be a numeric type (float or Decimal)
    - Format string 'f' must be a valid Python format string
    - 'no_grouping_separator' must be a boolean value
    
    Postconditions:
    - Returns a string representation of the number
    - Trailing zeros after decimal point are stripped
    - If no_grouping_separator is False, thousands separators are applied per locale
    - If no_grouping_separator is True, thousands separators are disabled
    - Empty string is returned when result would be just "." (edge case)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[format_decimal called] --> B{no_grouping_separator}
    B -- True --> C[locale.format_string with grouping=False]
    B -- False --> D[locale.format_string with grouping=True]
    C --> E[Remove trailing zeros]
    D --> E
    E --> F{Result is "."?}
    F -- Yes --> G[Return "" (empty string)]
    F -- No --> H[Return formatted string]
```

## Examples:
    >>> format_decimal(1234.5678)
    '1,234.568'
    
    >>> format_decimal(1234.5678, f='%.2f')
    '1,234.57'
    
    >>> format_decimal(1234.5678, no_grouping_separator=True)
    '1234.568'
    
    >>> format_decimal(0.0)
    '0'
    
    >>> format_decimal(-1234.5678)
    '-1,234.568'
    
    >>> format_decimal(1000.0)
    '1,000'
    
    >>> format_decimal(0.1000)
    '0.1'
```

## `csvkit.utilities.csvstat.get_type` · *function*

## Summary:
Returns the class name of the data type for a specified column in a table structure.

## Description:
Extracts and returns the class name of the data type associated with a specific column in a table. This utility function provides a standardized way to determine the underlying data type of a column for analysis and reporting purposes. It is commonly used in CSV statistics and data profiling operations to understand column characteristics.

## Args:
    table: A table object containing columns with data type information
    column_id: An identifier (typically integer index) for the target column
    **kwargs: Additional keyword arguments (currently unused in implementation)

## Returns:
    str: The class name of the data type for the specified column

## Raises:
    AttributeError: When table, table.columns, table.columns[column_id], or table.columns[column_id].data_type does not exist
    IndexError: When column_id is out of bounds for table.columns

## Constraints:
    Preconditions:
    - table must have a .columns attribute that supports indexing
    - column_id must be a valid index for table.columns
    - table.columns[column_id] must have a .data_type attribute
    - table.columns[column_id].data_type must have a __class__ attribute

    Postconditions:
    - Returns a string representing the class name of the column's data type
    - The returned string is the unqualified class name of the data type

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[get_type called] --> B{table.columns[column_id] exists?}
    B -- No --> C[AttributeError raised]
    B -- Yes --> D{data_type exists?}
    D -- No --> E[AttributeError raised]
    D -- Yes --> F{__class__ exists?}
    F -- No --> G[AttributeError raised]
    F -- Yes --> H[Return __class__.__name__]
```

## Examples:
    # Basic usage
    type_name = get_type(my_table, 0)  # Returns "String" for first column
    
    # With different column
    type_name = get_type(my_table, 2)  # Returns data type class name for third column

## `csvkit.utilities.csvstat.get_unique` · *function*

## Summary:
Returns the count of distinct values in a specified column of a CSV table.

## Description:
This utility function calculates the cardinality of a column by counting the number of unique values it contains. It is used in CSV statistical analysis to understand data diversity and identify potential duplicates or categorical distributions.

## Args:
    table: An agate Table object containing CSV data
    column_id: Identifier for the column to analyze (integer index or column name string)
    **kwargs: Additional keyword arguments (currently unused in implementation)

## Returns:
    int: The count of distinct values in the specified column

## Raises:
    KeyError: If column_id is a string that does not match any column name in the table
    IndexError: If column_id is an integer that is out of bounds for the table columns

## Constraints:
    Preconditions:
    - The table parameter must be a valid agate Table object
    - The column_id must reference an existing column in the table
    - The column_id must be a valid identifier for accessing table columns
    
    Postconditions:
    - Returns an integer representing the count of unique values
    - Does not modify the original table or its data

## Side Effects:
    None: This function performs no I/O operations or external state mutations

## Control Flow:
```mermaid
flowchart TD
    A[get_unique called] --> B{Valid table provided?}
    B -- Yes --> C{Valid column_id provided?}
    C -- Yes --> D[Access table.columns[column_id]]
    D --> E[Call values_distinct()]
    E --> F[Return len(values_distinct())]
    C -- No --> G[Raises KeyError/IndexError]
    B -- No --> G[Raises AttributeError]
```

## Examples:
    # Basic usage with column index
    unique_count = get_unique(my_table, 0)  # Count unique values in first column
    
    # Usage with column name
    unique_count = get_unique(my_table, 'email')  # Count unique email addresses
    
    # Typical usage in statistical analysis
    column_stats = {
        'unique_values': get_unique(my_table, 'category'),
        'total_rows': len(my_table)
    }
```

## `csvkit.utilities.csvstat.get_freq` · *function*

## Summary
Returns the most frequently occurring values in a specified table column along with their counts.

## Description
Extracts values from a specified column in a table and computes their frequency distribution, returning the top N most common values. This function is used to quickly analyze the distribution of values in categorical data columns.

## Args
    table: An agate.Table instance containing the data to analyze
    column_id: Identifier for the column to analyze (typically an integer index or column name)
    freq_count (int): Maximum number of top frequent values to return. Defaults to 5.
    **kwargs: Additional keyword arguments (currently unused in implementation)

## Returns
    list[dict]: A list of dictionaries, each containing:
        - 'value': The value found in the column
        - 'count': The number of occurrences of that value
    Returns an empty list if:
        - The column contains no values
        - freq_count is 0 or negative
        - The table is empty
        - column_id refers to a non-existent column

## Raises
    None explicitly raised in the function body

## Constraints
    Preconditions:
        - table must be a valid agate.Table instance
        - column_id must be a valid identifier for a column in the table
        - freq_count must be a non-negative integer
    
    Postconditions:
        - Returns a list of dictionaries with 'value' and 'count' keys
        - The list is sorted by count in descending order (most frequent first)
        - The length of the returned list is at most freq_count
        - If freq_count is 0, returns an empty list

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[get_freq called] --> B[table.columns[column_id].values()]
    B --> C[Counter(values)]
    C --> D[Counter.most_common(freq_count)]
    D --> E[Format results as list of dicts]
    E --> F[Return result]
```

## Examples
    # Get top 3 most frequent values from column 0
    result = get_freq(my_table, 0, freq_count=3)
    # Returns: [{'value': 'A', 'count': 15}, {'value': 'B', 'count': 8}, {'value': 'C', 'count': 3}]
    
    # Get all unique values with their counts (up to default limit of 5)
    result = get_freq(my_table, 'category_column')
    # Returns: [{'value': 'X', 'count': 20}, {'value': 'Y', 'count': 12}, ...] (top 5)
    
    # Get no results when freq_count is 0
    result = get_freq(my_table, 0, freq_count=0)
    # Returns: []
    
    # Handle empty table gracefully
    result = get_freq(empty_table, 0)
    # Returns: []

## `csvkit.utilities.csvstat.launch_new_instance` · *function*

## Summary:
Creates and executes a CSVStat utility instance to compute descriptive statistics for CSV file columns.

## Description:
This function serves as the entry point for launching the csvstat command-line utility. It instantiates the CSVStat class and invokes its run method to process CSV data according to the configured command-line arguments. The function abstracts away the instantiation and execution details, providing a clean interface for the csvkit framework to initialize and run the CSV statistical analysis utility.

This function follows the standard csvkit pattern where each command-line utility has a launch_new_instance function that creates and runs the appropriate utility class instance. It is typically called by the csvkit command-line entry points to initiate processing of CSV files with statistical analysis capabilities.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised by this function, though the underlying CSVStat.run() method may raise exceptions inherited from CSVKitUtility such as:
    - SystemExit: Raised by argparser.error() when invalid argument combinations are detected
    - ValueError: Raised by skip_lines() when skip_lines argument is not an integer
    - RequiredHeaderError: Raised by print_column_names() when --no-header-row is used with -n/--names options
    - UnicodeDecodeError: Handled by custom exception handler for encoding issues

## Constraints:
    Preconditions:
    - The csvkit command-line environment must be properly initialized
    - Command-line arguments must be available for parsing by CSVStat
    - Standard input/output streams must be accessible
    
    Postconditions:
    - The CSVStat utility will have processed input CSV data according to its configuration
    - Statistical output will be written to either stdout/stderr or specified output files
    - The process will exit with appropriate status codes based on processing results

## Side Effects:
    - Reads from standard input or specified input file(s)
    - Writes to standard output or specified output file(s)
    - May write diagnostic messages to standard error
    - Processes command-line arguments through the csvkit argument parser

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance called] --> B[Create CSVStat instance]
    B --> C[Call utility.run()]
    C --> D[CSVStat.run() inherits from CSVKitUtility.run()]
    D --> E[CSVStat parses command-line arguments]
    E --> F[CSVStat opens input file if needed]
    F --> G[CSVStat processes CSV data through main()]
    G --> H{Names only requested?}
    H -->|Yes| I[Print column names and exit]
    H -->|No| J{Count only requested?}
    J -->|Yes| K[Calculate and print row count]
    J -->|No| L[Parse column identifiers and operations]
    L --> M{Operations specified?}
    M -->|Yes| N[Print statistics for specified operations]
    M -->|No| O[Calculate and print full statistics for all columns]
    O --> P[Output statistics in selected format (text, CSV, JSON)]
    N --> P
    P --> Q[CSVStat closes files and exits]
```

## Examples:
```bash
# Basic usage to get all statistics for all columns
csvstat data.csv

# Get only mean and median for specific columns
csvstat -c 1,3 --mean --median data.csv

# Output as CSV format
csvstat --csv data.csv

# Display only column names and indices
csvstat -n data.csv

# Get row count only
csvstat --count data.csv

# Launch programmatically (equivalent to command-line invocation)
from csvkit.utilities.csvstat import launch_new_instance
launch_new_instance()
```

