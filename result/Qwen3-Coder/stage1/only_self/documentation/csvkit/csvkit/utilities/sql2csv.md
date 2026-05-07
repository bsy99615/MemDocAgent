# `sql2csv.py`

## `csvkit.utilities.sql2csv.SQL2CSV` · *class*

## Summary:
A command-line utility that executes SQL queries against databases and outputs results to CSV format.

## Description:
SQL2CSV is a CSVKit utility designed to execute SQL queries on database connections and output the resulting data to CSV format. It provides a flexible interface for running SQL commands against various database backends through SQLAlchemy, supporting both inline queries and query files. The utility integrates with the standard csvkit command-line framework, inheriting common CSV processing capabilities while specializing in database query execution.

This class should be instantiated when users need to convert database query results into CSV format. It is typically invoked through the command-line interface rather than directly by application code.

## State:
- `description` (str): Class variable describing the utility's purpose
- `override_flags` (list): List of argument flags that are overridden to customize behavior
- `argparser`: Argument parser instance inherited from CSVKitUtility
- `args`: Parsed command-line arguments
- `output_file`: Output file handle for CSV writing
- `input_file`: Input file handle for reading SQL query files
- `reader_kwargs`: CSV reader configuration parameters
- `writer_kwargs`: CSV writer configuration parameters

## Lifecycle:
Creation: Instances are created automatically by the CSVKit framework when parsing command-line arguments. The constructor initializes the argument parser and sets up standard CSV processing capabilities.

Usage: The utility follows the standard CSVKit pattern:
1. `run()` method is called by the framework to orchestrate execution
2. `add_arguments()` configures command-line options
3. `main()` executes the SQL query and writes results to CSV
4. Input/output files are managed automatically

Destruction: Cleanup occurs automatically through the CSVKit framework's resource management when the utility completes execution.

## Method Map:
```mermaid
graph TD
    A[run()] --> B[add_arguments()]
    A --> C[main()]
    C --> D[create_engine()]
    C --> E[engine.connect()]
    C --> F[exec_driver_sql()]
    C --> G[agate.csv.writer()]
    C --> H[output.writerow()]
    D --> I[ImportError handling]
    F --> J[rows.returns_rows check]
    J --> K[output.writerow(keys)]
    K --> L[output.writerow(row)]
```

## Raises:
- ImportError: When the required database backend is not installed for the specified connection string
- argparse.ArgumentError: When required arguments are missing (via argparser.error())
- UnicodeDecodeError: When input query file encoding is invalid (handled by parent class)

## Example:
```python
# Command-line usage:
# sql2csv --db postgresql://user:pass@localhost/mydb query.sql > output.csv
# sql2csv --db sqlite:///mydb.sqlite --query "SELECT * FROM users" > output.csv

# Programmatic usage (via CSVKit framework):
from csvkit.utilities.sql2csv import SQL2CSV
tool = SQL2CSV(['--db', 'sqlite:///example.db', 'query.sql'])
tool.run()
```

### `csvkit.utilities.sql2csv.SQL2CSV.add_arguments` · *method*

## Summary:
Configures command-line argument parsers for SQL2CSV utility to accept database connection strings, SQL query sources, encoding specifications, and header row options.

## Description:
This method extends the base CSVKitUtility argument parser to include SQL-specific command-line options. It defines arguments for connecting to databases, specifying SQL queries through files or stdin, setting input encoding, and controlling header row output. The method is called during the initialization phase of the CSVKitUtility lifecycle to build the complete argument parser before parsing user input.

The method is separated from the main logic to maintain clean code organization and follows the CSVKitUtility pattern where subclasses implement add_arguments() to customize their argument parsing while inheriting common CSV processing capabilities from the parent class.

## Args:
    self: The SQL2CSV instance whose argparser attribute is being modified

## Returns:
    None: This method modifies the instance's argparser in-place and returns nothing

## Raises:
    None: This method does not raise exceptions directly

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies the argument parser instance)

## Constraints:
    Preconditions: 
    - The SQL2CSV instance must have an argparser attribute initialized (inherited from CSVKitUtility)
    - The argparser must support add_argument() method calls
    
    Postconditions:
    - The argparser contains all SQL2CSV-specific command-line arguments
    - Default values are properly set for all arguments
    - Argument help text is available for usage display

## Side Effects:
    - Modifies the instance's argparser attribute by adding new arguments
    - Sets default values for various CSV-related arguments through set_defaults()

### `csvkit.utilities.sql2csv.SQL2CSV.main` · *method*

## Summary:
Executes an SQL query against a database and outputs the results as CSV-formatted data.

## Description:
This method orchestrates the complete workflow for executing SQL queries and converting results to CSV format. It handles connection establishment, query input processing (from command-line arguments, files, or stdin), database execution, and CSV output generation. The method serves as the core execution point for the sql2csv utility.

The method follows these stages:
1. Validates input requirements (requires either query argument or input file/stdin)
2. Establishes database connection using SQLAlchemy
3. Processes SQL query from either command-line argument or file/stdin input
4. Executes the query against the database
5. Writes results to output file as CSV, including headers when appropriate

Known callers:
- CSVKitUtility.run(): Called during the standard execution lifecycle when the utility's run() method is invoked
- This method is part of the standard CSVKit utility execution flow where run() calls main() after setting up input/output streams

This logic is encapsulated in its own method because it represents a complete, self-contained workflow that needs to be reusable across different execution contexts while maintaining separation of concerns between input processing, database operations, and output formatting.

## Args:
    None: This method operates on instance attributes and does not accept explicit parameters.

## Returns:
    None: This method performs side effects (database operations and file I/O) but does not return a value.

## Raises:
    ImportError: When the required database backend is not installed for the specified connection string
    SystemExit: When additional input is expected but not provided (via argparser.error())

## State Changes:
    Attributes READ:
    - self.args.connection_string: Database connection string for SQLAlchemy
    - self.args.query: SQL query provided as command-line argument
    - self.args.input_path: Path to SQL query file
    - self.args.no_header_row: Flag indicating whether to suppress column headers
    - self.writer_kwargs: CSV writer configuration parameters
    - self.args.encoding: Encoding for input file processing
    
    Attributes WRITTEN:
    - self.input_file: File handle for input query file (when reading from file)
    - self.output_file: File handle for CSV output (inherited from parent)

## Constraints:
    Preconditions:
    - self.args must be initialized (typically during object construction)
    - Database connection string must be valid and backend must be installed
    - Either --query argument must be provided or input file must be available
    - Connection string must specify a supported database backend
    
    Postconditions:
    - Database connection is properly established and disposed
    - Query is executed and results are written to output file
    - Input file handle is properly closed when used
    - Output file handle remains open for further writes (if needed)

## Side Effects:
    - Opens and closes database connections using SQLAlchemy
    - Reads from input file or stdin when no --query argument is provided
    - Writes to output file in CSV format
    - May raise SystemExit when validation fails
    - Uses agate.csv.writer for CSV output formatting
    - Calls argparser.error() for validation failures

## `csvkit.utilities.sql2csv.launch_new_instance` · *function*

## Summary:
Creates and executes a new SQL2CSV utility instance to run SQL queries against databases and output results to CSV format.

## Description:
This function serves as the entry point for launching the SQL2CSV command-line utility. It instantiates a SQL2CSV object and invokes its run() method to process command-line arguments and execute database queries, converting the results into CSV format. The function follows the standard csvkit pattern where command-line utilities are instantiated and executed through a dedicated launch function.

This logic is extracted into its own function rather than being inlined in the main module to enable:
- Consistent instantiation pattern across different invocation contexts
- Testability of the utility creation and execution flow
- Separation of concerns between utility creation and execution
- Support for alternative launch mechanisms (like in unit tests or other entry points)

## Args:
    None

## Returns:
    None

## Raises:
    SystemExit: Raised by SQL2CSV.run() when argument validation fails or when the utility encounters fatal errors during execution
    ImportError: Raised when required database backend is not installed for the specified connection string
    Various exceptions from file I/O operations handled by the parent CSVKitUtility class
    UnicodeDecodeError: Potentially raised during SQL query file reading if encoding issues occur (handled by parent class)

## Constraints:
    Preconditions:
    - Command-line arguments must be available via sys.argv for parsing
    - Standard input/output streams must be accessible
    - Required CSV processing dependencies must be available
    - Input files (if specified) must be readable
    - Database connection strings (if specified) must be valid and accessible
    
    Postconditions:
    - A SQL2CSV utility instance is created and executed
    - SQL queries are executed against the specified database
    - Query results are written to CSV format in stdout or specified output file
    - All temporary resources are properly cleaned up

## Side Effects:
    - Reads from standard input or specified input files (via CSVKitUtility's input_file handling)
    - Writes CSV output to standard output or specified output file (via CSVKitUtility's output_file handling)
    - Processes command-line arguments from sys.argv through CSVKitUtility's argument parser
    - May establish database connections when --db flag is specified
    - May read from files specified via --query flag when executing SQL queries
    - May modify database state when --insert flag is used with database connections

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[Create SQL2CSV() instance]
    B --> C[Call utility.run()]
    C --> D{Input file handling}
    D -->|File specified| E[Open input file]
    D -->|No file| F[Use stdin]
    E --> G[Parse command-line arguments]
    F --> G
    G --> H{Validation checks}
    H -->|Invalid args| I[Display error and exit]
    H -->|Valid args| J[Process SQL query]
    J --> K{Database connection requested?}
    K -->|Yes| L[Create database engine]
    K -->|No| M[Skip database connection]
    L --> N[Establish database connection]
    N --> O[Execute SQL query]
    O --> P{Query returns rows?}
    P -->|Yes| Q[Write header row]
    Q --> R[Write data rows]
    P -->|No| S[Skip row writing]
    R --> T[Write to output]
    S --> T
    T --> U[Cleanup and exit]
```

## Examples:
```bash
# Execute SQL query against PostgreSQL database and output to CSV
sql2csv --db postgresql://user:pass@localhost/mydb "SELECT * FROM users" > output.csv

# Execute SQL query from file against SQLite database
sql2csv --db sqlite:///mydb.sqlite query.sql > output.csv

# Execute query with custom CSV output settings
sql2csv --db mysql://user:pass@localhost/mydb --delimiter ';' "SELECT * FROM products" > output.csv

# Execute query and insert results into database
sql2csv --db postgresql://user:pass@localhost/mydb --insert "SELECT * FROM source_table" > /dev/null
```

