# `sql2csv.py`

## `csvkit.utilities.sql2csv.SQL2CSV` · *class*

## Summary:
SQL2CSV is a command-line utility that executes SQL queries against databases and outputs the results as CSV formatted data.

## Description:
SQL2CSV enables users to run SQL queries on various database backends and export the resulting tabular data to CSV format. It serves as a bridge between database systems and CSV processing workflows, supporting both inline queries and query files. The utility integrates with SQLAlchemy for database connectivity and uses agate for CSV output formatting.

The utility inherits from CSVKitUtility, which provides common argument parsing, file handling, and execution orchestration. SQL2CSV specifically implements the main processing logic for database query execution and CSV output generation.

## State:
- connection_string (str): Database connection string, defaults to 'sqlite://'
- input_path (str): Path to file containing SQL query, or None if using stdin/piped data
- query (str): SQL query string, either from --query flag or file/stdin content
- no_header_row (bool): Flag indicating whether to omit column header row in output
- encoding (str): Text encoding for reading query files, defaults to 'utf-8'
- engine: SQLAlchemy Engine instance created from connection_string
- connection: SQLAlchemy Connection instance for executing queries
- rows: Result set from query execution
- output_file: File-like object for writing CSV output
- input_file: File-like object for reading SQL query content

## Lifecycle:
- Creation: Instantiate with optional command-line arguments and output file handle
- Usage: Call run() method which:
  1. Parses command-line arguments via add_arguments()
  2. Validates input requirements using additional_input_expected()
  3. Establishes database connection using SQLAlchemy create_engine()
  4. Reads SQL query from --query flag, file, or stdin
  5. Executes query and writes results to CSV format using agate.csv.writer
  6. Cleans up database connections and file handles
- Destruction: Automatic cleanup of database connections and file handles via run() method's execution flow

## Method Map:
```mermaid
graph TD
    A[SQL2CSV.run] --> B[CSVKitUtility.run]
    B --> C[additional_input_expected]
    C --> D{Input expected?}
    D -->|Yes| E[argparser.error]
    D -->|No| F[create_engine]
    F --> G[engine.connect]
    G --> H{Query from --query?}
    H -->|Yes| I[Use query string]
    H -->|No| J[Open input file]
    J --> K[Read query lines]
    K --> L[connection.exec_driver_sql]
    L --> M{Returns rows?}
    M -->|Yes| N[Write header row]
    N --> O[Write data rows]
    M -->|No| P[Skip output]
    O --> Q[connection.close]
    Q --> R[engine.dispose]
```

## Raises:
- ImportError: When required database backend is not installed for the specified connection string
- SystemExit: When required input is missing (via argparser.error)
- Exception: Various database-related exceptions from SQLAlchemy operations

## Example:
```python
# Execute query from file
sql2csv = SQL2CSV(['--db', 'postgresql://user:pass@localhost/db', 'query.sql'])
sql2csv.run()

# Execute inline query
sql2csv = SQL2CSV(['--db', 'mysql://user:pass@localhost/db', '--query', 'SELECT * FROM users'])
sql2csv.run()

# Skip header row
sql2csv = SQL2CSV(['--db', 'sqlite:///example.db', '--no-header-row', 'query.sql'])
sql2csv.run()
```

### `csvkit.utilities.sql2csv.SQL2CSV.add_arguments` · *method*

## Summary:
Configures command-line arguments for the SQL to CSV conversion utility.

## Description:
This method initializes all command-line argument parsers for the sql2csv utility. It defines the available options and positional arguments that users can specify when running the command-line tool. The method is part of the CSVKitUtility framework and sets up the argument parser before program execution begins. It establishes the interface for specifying database connections, input sources, encoding preferences, and output formatting options.

The method adds several key arguments:
- Database connection string (--db) with sqlite:// as default
- Input file specification (positional argument) with optional file argument
- SQL query specification (--query) that overrides file input
- Encoding specification (-e/--encoding) with utf-8 as default
- Header row control (-H/--no-header-row) to suppress column names

## Args:
    None directly - operates on self.argparser instance

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: Must be called on an instance of SQL2CSV class with initialized argparser attribute
    Postconditions: The self.argparser instance contains all defined command-line arguments and their configurations

## Side Effects:
    Modifies the self.argparser instance by adding multiple argument definitions
    Sets default values for various CSV writing parameters through set_defaults call

### `csvkit.utilities.sql2csv.SQL2CSV.main` · *method*

## Summary:
Executes an SQL query against a database and writes the results to CSV format.

## Description:
This method serves as the main execution entry point for the sql2csv utility. It connects to a database using the provided connection string, executes an SQL query (either from command-line arguments or from a file/stdin), and outputs the results to CSV format. The method handles both direct query input and file-based query input, managing database connections and CSV output formatting appropriately. It validates input requirements and provides detailed error messages for missing database backends.

## Args:
    self: The instance of SQL2CSV class containing configuration and state

## Returns:
    None

## Raises:
    ImportError: When the required database backend is not installed for the specified connection string
    SystemExit: When additional input is expected but not provided (via argparser.error)

## State Changes:
    Attributes READ: 
        - self.args.connection_string
        - self.args.query
        - self.args.input_path
        - self.args.no_header_row
        - self.args.encoding
        - self.writer_kwargs
        - self.output_file (inherited from parent class)
    Attributes WRITTEN: 
        - self.input_file (temporary file handle for reading query from file)

## Constraints:
    Preconditions:
        - Database connection string must be valid and accessible
        - Either a query argument must be provided or input file/stdin must be available
        - Required database backend must be installed for the connection string
        - Input file path must be readable if specified
        - Output file must be writable
        - If stdin is connected to a terminal, an input file or query must be provided
        
    Postconditions:
        - Database connection is properly closed
        - Engine resources are disposed
        - Output file contains properly formatted CSV data
        - Temporary input file handle is closed
        - All input streams are properly managed and closed

## Side Effects:
    - Opens and closes database connections using SQLAlchemy
    - Reads from input files or stdin
    - Writes to output file using agate's CSV writer
    - May reconfigure stdin encoding when reading from stdin
    - Calls argparser.error() which exits the program on validation failure
    - Uses LazyFile wrapper for efficient file handling

## `csvkit.utilities.sql2csv.launch_new_instance` · *function*

## Summary:
Creates and runs a new instance of the SQL2CSV utility to execute SQL queries and output results as CSV.

## Description:
This function serves as a factory and execution launcher for the SQL2CSV command-line utility. It instantiates a SQL2CSV object with default configuration and immediately invokes its run() method to process SQL queries and generate CSV output. The function encapsulates the typical usage pattern of creating a utility instance and executing it, making it convenient for command-line interface integration and testing.

This logic is extracted into its own function rather than being inlined because it provides a clean abstraction for launching the utility, separates instantiation from execution concerns, and allows for easier testing and reuse of the utility creation pattern. The SQL2CSV.run() method handles cleanup of database connections and file handles automatically.

## Args:
    None

## Returns:
    None

## Raises:
    Any exceptions that may occur during SQL2CSV instantiation or execution, including:
    - ImportError: When required database backend is not installed
    - SystemExit: When required input validation fails
    - Exception: Various database or I/O related exceptions from SQLAlchemy or agate operations

## Constraints:
    Preconditions:
        - The SQL2CSV class must be properly imported and available
        - Command-line arguments must be accessible via sys.argv or equivalent
        - Required database drivers must be installed for the specified connection string
        - Output destination must be writable

    Postconditions:
        - A SQL2CSV instance is created and executed
        - All database connections and file handles are properly cleaned up by SQL2CSV.run()
        - CSV output is written to the configured output destination

## Side Effects:
    - Creates a SQL2CSV instance
    - Invokes the run() method which opens database connections
    - Reads SQL query from stdin, file, or command-line arguments
    - Writes CSV-formatted output to stdout or configured output file
    - May close stdin if reading from terminal
    - May raise SystemExit if input validation fails
    - Automatically cleans up database connections and file handles upon completion

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance] --> B[Create SQL2CSV()]
    B --> C[utility.run()]
    C --> D{SQL2CSV.run()}
    D --> E[Parse args via CSVKitUtility.run]
    E --> F{Additional input expected?}
    F -->|Yes| G[Exit with error]
    F -->|No| H[Create SQLAlchemy engine]
    H --> I[Connect to database]
    I --> J{Query from --query?}
    J -->|Yes| K[Use query string]
    J -->|No| L[Read query from file/stdin]
    L --> M[Execute query]
    M --> N{Results returned?}
    N -->|Yes| O[Write header row]
    O --> P[Write data rows]
    N -->|No| Q[Skip output]
    P --> R[Close connection]
    R --> S[Dispose engine]
```

## Examples:
```python
# Typical usage in command-line context
launch_new_instance()

# Equivalent manual approach
utility = SQL2CSV()
utility.run()
```

