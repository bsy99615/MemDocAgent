# `sql2csv.py`

## `csvkit.utilities.sql2csv.SQL2CSV` · *class*

## Summary:
A command-line utility for executing SQL queries against databases and outputting results to CSV format.

## Description:
The SQL2CSV class implements a CSVKit utility that allows users to execute SQL queries on various database backends and output the results to CSV format. It serves as a bridge between database systems and CSV file generation, supporting both inline queries and query files. The class integrates with the CSVKit CLI framework to provide standardized command-line argument handling and output formatting.

This utility is particularly useful for database administrators, data analysts, and developers who need to extract data from databases in a portable CSV format. It supports multiple database backends through SQLAlchemy's connection system and provides flexible output formatting options.

## State:
- `args`: Parsed command-line arguments containing database connection info, query source, and formatting options
- `output_file`: File-like object for writing CSV output (defaults to stdout)
- `input_file`: File-like object for reading SQL query input (when reading from file)
- `connection_string`: Database connection string parsed from --db argument (default: sqlite://)
- `query`: SQL query string constructed from either --query argument or input file content
- `writer_kwargs`: Dictionary of CSV writer configuration parameters extracted from CLI arguments

## Lifecycle:
1. **Creation**: Instantiated by the CSVKit framework when invoked from command line
2. **Usage**: Called via the `run()` method inherited from CSVKitUtility, which internally calls `main()`
3. **Execution Flow**:
   - Validates input requirements (query source provided)
   - Establishes database connection using SQLAlchemy
   - Reads SQL query from --query argument or input file/stdin
   - Executes query using database engine
   - Writes results to CSV output with optional header row
4. **Destruction**: Automatically closes database connections and disposes engine resources

## Method Map:
```mermaid
graph TD
    A[SQL2CSV.run()] --> B[SQL2CSV.main()]
    B --> C[Validate input requirements]
    C --> D[Create SQLAlchemy engine]
    D --> E[Establish database connection]
    E --> F[Read SQL query]
    F --> G[Execute query with exec_driver_sql]
    G --> H{Query returns rows?}
    H -->|Yes| I[Write header row if enabled]
    I --> J[Write result rows]
    H -->|No| K[Skip row writing]
    J --> L[Close connection]
    K --> L
    L --> M[Dispose engine]
```

## Raises:
- `ImportError`: Raised when required database backend is not installed for the specified connection string
- `argparse.ArgumentError`: Raised when required input is missing (no query source provided)
- Any exceptions raised by file I/O operations when reading query from file
- Any exceptions raised by database operations during query execution

## Example:
```bash
# Execute a query directly
python sql2csv.py --db "postgresql://user:pass@localhost/db" --query "SELECT * FROM users LIMIT 10"

# Execute a query from a file
python sql2csv.py --db "mysql://user:pass@localhost/db" query.sql

# Execute a query with no header row
python sql2csv.py --db "sqlite:///data.db" --query "SELECT id, name FROM products" --no-header-row

# Pipe query from stdin
echo "SELECT COUNT(*) FROM orders;" | python sql2csv.py --db "sqlite:///data.db"
```

### `csvkit.utilities.sql2csv.SQL2CSV.add_arguments` · *method*

## Summary:
Configures command-line arguments for SQL-to-CSV conversion utility, defining database connections, query sources, and output formatting options.

## Description:
This method extends the base CSVKitUtility argument parser to include SQL-specific command-line options. It enables users to specify database connection strings, input query files, inline SQL queries, encoding preferences, and header row behavior. The method is part of the standard CSVKitUtility lifecycle where argument parsing occurs during initialization.

## Args:
    self: The SQL2CSV instance whose argparser is being configured

## Returns:
    None: This method modifies the instance's argument parser in-place

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies the argument parser configuration)

## Constraints:
    Preconditions: 
    - Must be called on an instance of SQL2CSV class
    - Instance must have an argparser attribute (inherited from CSVKitUtility)
    
    Postconditions:
    - self.argparser contains all SQL2CSV-specific command-line arguments
    - Default values are set for CSV processing parameters

## Side Effects:
    None: This method only configures argument parsing and doesn't perform I/O operations or modify external state

### `csvkit.utilities.sql2csv.SQL2CSV.main` · *method*

## Summary:
Converts SQL query results to CSV format by connecting to a database, executing a query, and writing the output to a file or stdout.

## Description:
This method serves as the core execution point for the sql2csv utility, transforming database query results into CSV format. It is called during the execution phase of CSVKit utilities when processing SQL-to-CSV conversion requests. The method handles both direct SQL query input via command-line arguments and file-based query input, managing database connections, query execution, and CSV output formatting with proper header handling.

## Args:
    self: The SQL2CSV instance containing configuration and state

## Returns:
    None: This method performs I/O operations and does not return a value

## Raises:
    SystemExit: Raised by argparser.error() when additional input is expected but no query is provided
    ImportError: Raised when the required database backend is not installed for the specified connection string

## State Changes:
    Attributes READ: 
    - self.args.connection_string: Database connection string for SQLAlchemy engine creation
    - self.args.query: SQL query string when provided directly
    - self.args.input_path: Input file path when query is read from file
    - self.args.no_header_row: Flag to control header row inclusion in output
    - self.additional_input_expected(): Method to determine if stdin input is expected
    - self.output_file: Output file handle for CSV writing
    - self.writer_kwargs: Keyword arguments for CSV writer configuration
    Attributes WRITTEN: 
    - self.input_file: Set when reading query from file input

## Constraints:
    Preconditions:
    - Database connection string must be valid and backend must be installed
    - If additional input is expected (interactive mode), either a query must be provided via --query or an input file must be specified
    - Query must be executable against the target database
    Postconditions:
    - Database connections are properly closed and disposed
    - Output file is properly written with CSV data
    - Input file is properly closed when read from

## Side Effects:
    - Opens and closes database connections using SQLAlchemy
    - Reads from input file when query is provided via file
    - Writes to output file or stdout in CSV format
    - May raise ImportError if database backend is missing
    - Calls argparser.error() which terminates the program with error code

## `csvkit.utilities.sql2csv.launch_new_instance` · *function*

## Summary:
Creates and executes a new instance of the SQL2CSV command-line utility for executing SQL queries against databases and outputting results to CSV format.

## Description:
This function serves as the entry point for launching the SQL2CSV command-line utility. It instantiates a SQL2CSV object and invokes its run method to process command-line arguments and execute SQL queries against database systems, outputting the results in CSV format. The function follows the standard csvkit utility pattern where each command-line tool provides a launch_new_instance function that handles instantiation and execution.

The SQL2CSV utility is particularly useful for database administrators, data analysts, and developers who need to extract data from databases in a portable CSV format. It supports multiple database backends through SQLAlchemy's connection system and provides flexible output formatting options.

## Args:
    None

## Returns:
    None

## Raises:
    SystemExit: Raised by SQL2CSV's argument parser when command-line argument validation fails or when required input is missing
    ImportError: Raised when required database backend libraries are missing for the specified connection string
    argparse.ArgumentError: Raised when required input is missing (no query source provided)
    Any exceptions raised by file I/O operations when reading query from file
    Any exceptions raised by database operations during query execution

## Constraints:
    Preconditions:
    - The function assumes that the csvkit command-line framework is properly initialized
    - Command-line arguments must be available for parsing (typically via sys.argv)
    - Database connection strings (if specified) must be compatible with SQLAlchemy
    - Input file paths (if specified) must be accessible
    
    Postconditions:
    - A SQL2CSV instance is created and executed
    - Command-line arguments are parsed and processed
    - SQL query is executed against the specified database
    - Results are written to CSV output (stdout by default)

## Side Effects:
    - Reads from stdin or specified input file when processing SQL query input
    - Writes CSV output to stdout or specified output file
    - Establishes database connections via SQLAlchemy when a database connection is specified
    - May read command-line arguments from sys.argv
    - Closes database connections and disposes engine resources upon completion

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[SQL2CSV().__init__()]
    B --> C[utility.run()]
    C --> D[CSVKitUtility.run()]
    D --> E[Parse command-line arguments]
    E --> F{Database connection specified?}
    F -->|Yes| G[Establish database connection]
    F -->|No| H[Skip database connection]
    G --> I[Open input files]
    H --> I
    I --> J[Validate arguments]
    J --> K{Query source provided?}
    K -->|No| L[SystemExit]
    K -->|Yes| M[Execute SQL query]
    M --> N{Query returns rows?}
    N -->|Yes| O[Write header row if enabled]
    O --> P[Write result rows]
    N -->|No| Q[Skip row writing]
    P --> R[Close database connection]
    Q --> R
    R --> S[Dispose engine]
    S --> T[End execution]
```

## Examples:
```bash
# Execute a query directly
python sql2csv.py --db "postgresql://user:pass@localhost/db" --query "SELECT * FROM users LIMIT 10"

# Execute a query from a file
python sql2csv.py --db "mysql://user:pass@localhost/db" query.sql

# Execute a query with no header row
python sql2csv.py --db "sqlite:///data.db" --query "SELECT id, name FROM products" --no-header-row

# Pipe query from stdin
echo "SELECT COUNT(*) FROM orders;" | python sql2csv.py --db "sqlite:///data.db"
```

