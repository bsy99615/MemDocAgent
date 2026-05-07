# `sql2csv.py`

## `csvkit.utilities.sql2csv.SQL2CSV` · *class*

*No documentation generated.*

### `csvkit.utilities.sql2csv.SQL2CSV.add_arguments` · *method*

## Summary:
Configures command-line arguments for the SQL2CSV utility, enabling database connections, SQL query execution, and CSV output formatting.

## Description:
This method extends the base CSVKitUtility argument parser to include SQL-specific command-line options. It adds arguments for specifying database connection strings, SQL query input sources (file, stdin, or inline), encoding settings, and CSV output formatting controls. The method is called during the initialization phase of the SQL2CSV utility to set up the complete command-line interface before argument parsing occurs.

The method enables users to execute SQL queries against databases and output results as CSV files. It provides flexibility in how SQL queries are provided (as files, piped stdin, or inline), supports various database backends through SQLAlchemy, and allows customization of CSV output characteristics.

## Args:
    self: The SQL2CSV instance whose argument parser will be modified.

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: 
        - self.argparser: The argument parser instance being modified
    Attributes WRITTEN:
        - self.argparser: Modified to include database connection, query input, and CSV formatting arguments

## Constraints:
    Preconditions:
        - The instance must have completed initialization of `self.argparser` (typically via `_init_common_parser()`)
        - The method should only be called during object initialization, not after argument parsing
    Postconditions:
        - The argument parser contains both common CSV arguments and SQL2CSV-specific arguments

## Side Effects:
    None

### `csvkit.utilities.sql2csv.SQL2CSV.main` · *method*

## Summary:
Executes SQL query execution and CSV output generation from database results.

## Description:
Processes SQL queries from command-line arguments, input files, or stdin, executes them against a configured database, and writes the resulting rows to CSV format. This method serves as the core execution logic for the sql2csv utility, handling database connection management, query parsing, and CSV output formatting.

The method supports three input modes:
1. Direct query via --query argument
2. Query from file specified by positional argument
3. Query from piped stdin data

Known callers:
- CSVKitUtility.run(): Called during the standard execution lifecycle of CSVKit utilities
- Invoked as part of the command-line workflow where the utility processes SQL input and generates CSV output

This logic is separated into its own method to allow for proper inheritance and extension by subclasses while maintaining the standard CSVKitUtility execution pattern.

## Args:
    self: The SQL2CSV instance containing command-line arguments and state.

## Returns:
    None: This method does not return a value.

## Raises:
    ImportError: When the required database backend is not installed for the specified connection string
    SystemExit: When additional input is expected but not provided (via argparser.error)

## State Changes:
    Attributes READ:
        - self.args.connection_string: Database connection string for SQLAlchemy engine creation
        - self.args.query: SQL query string when provided directly
        - self.args.input_path: File path containing SQL query when not using --query
        - self.args.no_header_row: Flag controlling header row inclusion in output
        - self.args.encoding: Encoding for input file reading
        - self.writer_kwargs: CSV writer configuration parameters
        - self.output_file: Destination for CSV output
        - self.input_file: Input file handle for SQL query when reading from file
        - self.argparser: Error reporting mechanism for invalid input combinations

    Attributes WRITTEN:
        - self.input_file: Set when opening input file for SQL query reading

## Constraints:
    Preconditions:
        - self.args.connection_string must be a valid SQLAlchemy connection string
        - If additional input is expected (determined by additional_input_expected()), either --query must be provided or input must come from stdin/file
        - Database backend for connection string must be installed
        - self.output_file must be a valid writable file-like object
        - self.writer_kwargs must contain valid CSV writer parameters

    Postconditions:
        - Database connection and engine are properly closed
        - All resources are cleaned up regardless of success or failure
        - CSV output is written to self.output_file with appropriate headers and rows

## Side Effects:
    - Opens and closes database connections using SQLAlchemy
    - Reads from input file or stdin when no --query is provided
    - Writes to output file in CSV format using agate
    - May reconfigure stdin encoding when reading from terminal
    - Creates SQLAlchemy engine and connection objects
    - Disposes of database engine resources

## `csvkit.utilities.sql2csv.launch_new_instance` · *function*

## Summary:
Creates and executes a new instance of the SQL2CSV utility for converting SQL query results to CSV format.

## Description:
This function serves as a factory and execution wrapper for creating and running an instance of the SQL2CSV command-line utility. It instantiates the SQL2CSV class and invokes its run() method to process SQL queries and output results as CSV files. This abstraction allows for clean instantiation and execution of the utility while maintaining the standard csvkit command-line interface patterns.

The function is typically called during program initialization or when the sql2csv utility is invoked from the command line, providing a standardized way to launch the SQL-to-CSV conversion functionality.

## Args:
    None

## Returns:
    None

## Raises:
    Exceptions are not raised directly by this function, but may be propagated from the underlying SQL2CSV.run() method during execution including:
    - argparse.ArgumentError: When invalid command-line arguments are provided
    - IOError: When input/output files cannot be accessed
    - sqlalchemy.exc.*: When database connection issues occur
    - csv.Error: When CSV writing operations fail

## Constraints:
    Preconditions:
    - The SQL2CSV class must be properly imported and available in scope
    - Command-line arguments must be properly formatted if being processed from argv
    
    Postconditions:
    - A SQL2CSV instance is created and executed
    - Standard CSVKit utility lifecycle is followed (argument parsing, file handling, processing, output)

## Side Effects:
    - Reads input SQL query from file or stdin when applicable
    - Writes CSV output to stdout or specified output file
    - Establishes database connections using SQLAlchemy
    - May read configuration files or environment variables for database connections
    - May modify global state through argument parsing and CSV processing

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance called] --> B[Create SQL2CSV instance]
    B --> C[Call utility.run()]
    C --> D[Parse command-line arguments]
    D --> E{Input validation}
    E -->|Invalid| F[Display error and exit]
    E -->|Valid| G[Establish database connection]
    G --> H[Execute SQL query]
    H --> I{Query returns rows}
    I -->|Yes| J[Write header row if enabled]
    J --> K[Write data rows]
    K --> L[Close connections]
    I -->|No| M[Skip row writing]
    M --> L
    L --> N[Exit cleanly]
```

## Examples:
```python
# Typical usage when invoked from command line
# sql2csv --db postgresql://user:pass@localhost/dbname query.sql

# Programmatic usage
from csvkit.utilities.sql2csv import launch_new_instance
launch_new_instance()
```

