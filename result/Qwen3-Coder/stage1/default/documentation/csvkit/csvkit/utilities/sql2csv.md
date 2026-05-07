# `sql2csv.py`

## `csvkit.utilities.sql2csv.SQL2CSV` · *class*

## Summary:
A command-line utility that executes SQL queries against databases and outputs results to CSV format.

## Description:
SQL2CSV is a CSVKit utility designed to execute SQL queries on database connections and output the resulting data to CSV format. It serves as a bridge between database systems and CSV file processing, allowing users to extract query results into tabular CSV format for further analysis or processing. The utility supports both inline SQL queries via the --query flag and SQL script files via input file arguments.

This class is typically instantiated by the csvkit command-line framework when invoked as 'sql2csv' and should not be manually instantiated outside of this context.

## State:
- connection_string (str): Database connection string, defaults to 'sqlite://' 
- input_path (str): Path to SQL query file, or None if using stdin
- query (str): SQL query string, either from --query flag or file content
- no_header_row (bool): Flag indicating whether to omit column headers from output
- encoding (str): File encoding for SQL query files, defaults to 'utf-8'
- engine: SQLAlchemy engine instance created from connection_string
- connection: Database connection object from engine
- rows: Result set from executing SQL query
- output_file: File-like object for CSV output
- input_file: File handle for SQL query input (when reading from file)

## Lifecycle:
Creation: Automatically instantiated by csvkit framework when running 'sql2csv' command. Arguments are parsed through CSVKitUtility's argument parser.

Usage: The utility follows the standard CSVKitUtility lifecycle:
1. Arguments are parsed via add_arguments() and main() method
2. Database connection is established using SQLAlchemy
3. SQL query is read from --query flag, input file, or stdin
4. Query is executed against database
5. Results are written to output CSV file
6. Database connections are explicitly closed in main() method

Destruction: Database connections are explicitly closed via connection.close() and engine.dispose() calls in the main() method to ensure proper resource cleanup.

## Method Map:
```mermaid
graph TD
    A[SQL2CSV.add_arguments] --> B[CSVKitUtility.add_arguments]
    B --> C[SQL2CSV.main]
    C --> D[create_engine]
    D --> E[engine.connect]
    E --> F[SQL2CSV._open_input_file]
    F --> G[rows.exec_driver_sql]
    G --> H[agate.csv.writer]
    H --> I[output.writerow]
    I --> J[connection.close]
    J --> K[engine.dispose]
```

## Raises:
- ImportError: Raised when required database backend is not installed for the specified connection string
- argparse.ArgumentError: Raised when required input is missing (no query, file, or stdin data)
- sqlalchemy.exc.*: Various SQLAlchemy exceptions that may occur during database operations
- IOError: Raised when input file cannot be opened or read
- csv.Error: Raised when CSV writing fails

## Example:
```bash
# Execute SQL query directly
sql2csv --db postgresql://user:pass@localhost/mydb --query "SELECT * FROM users LIMIT 10"

# Execute SQL from file
sql2csv --db mysql://user:pass@localhost/mydb query.sql > output.csv

# Execute SQL from stdin
echo "SELECT COUNT(*) FROM users;" | sql2csv --db sqlite:///mydb.sqlite
```

### `csvkit.utilities.sql2csv.SQL2CSV.add_arguments` · *method*

## Summary:
Configures command-line arguments for the SQL2CSV utility to execute SQL queries and output results as CSV format.

## Description:
This method extends the base argument parser to include SQL-specific command-line options for connecting to databases, specifying SQL queries, and controlling CSV output formatting. It enables users to execute SQL queries against various database backends and export results to CSV format with customizable options.

The method is called during the initialization phase of the CSVKitUtility framework, allowing subclasses to define their specific command-line interface before parsing begins. This separation of concerns ensures consistent argument handling while allowing specialized functionality.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: 
        - self.argparser: The argument parser instance to configure
    Attributes WRITTEN: 
        - self.argparser: Configured with new command-line arguments

## Constraints:
    Preconditions:
        - The SQL2CSV instance must be properly initialized with an argument parser
        - The self.argparser attribute must be accessible and mutable
    Postconditions:
        - The argument parser contains all SQL2CSV-specific command-line options
        - Default values are set for CSV processing parameters

## Side Effects:
    None

### `csvkit.utilities.sql2csv.SQL2CSV.main` · *method*

*No documentation generated.*

## `csvkit.utilities.sql2csv.launch_new_instance` · *function*

## Summary:
Creates and executes a new instance of the SQL2CSV command-line utility for executing SQL queries against databases and outputting results to CSV format.

## Description:
This function serves as the entry point for launching the sql2csv command-line utility. It instantiates the SQL2CSV class and invokes its run method to process SQL queries against database connections and output the results to CSV format. The function abstracts away the instantiation and execution details, providing a clean interface for the csvkit framework to initialize and run the SQL-to-CSV conversion utility.

This function follows the standard csvkit pattern where each command-line utility has a launch_new_instance function that creates and runs the appropriate utility class instance. It is typically called by the csvkit command-line entry points to initiate processing of SQL queries with database operations and CSV output capabilities.

## Args:
    None

## Returns:
    None

## Raises:
    SystemExit: Raised by SQL2CSV.run() when argument validation fails or when the utility completes execution with exit status
    Various exceptions: Potentially raised by underlying database operations, CSV processing, or argument parsing methods during execution

## Constraints:
    Preconditions:
    - The csvkit command-line environment must be properly initialized
    - Command-line arguments must be available for parsing by SQL2CSV
    - Standard input/output streams must be accessible
    - Required database backend drivers must be installed for the specified connection string
    
    Postconditions:
    - The SQL2CSV utility will have processed SQL queries according to its configuration
    - Database connections will be properly established and closed
    - Output will be written to either stdout/stderr or specified output files
    - The process will exit with appropriate status codes based on processing results

## Side Effects:
    - Reads from standard input or specified input file(s) containing SQL queries
    - Writes to standard output or specified output file(s) with CSV formatted results
    - Establishes database connections when --db flag is used
    - May execute SQL queries against databases
    - Processes command-line arguments through the csvkit argument parser
    - May close database connections and dispose of SQLAlchemy engines

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance called] --> B[Create SQL2CSV instance]
    B --> C[Call utility.run()]
    C --> D[SQL2CSV.run() inherits from CSVKitUtility.run()]
    D --> E[SQL2CSV.main() executes]
    E --> F{Input validation and argument parsing}
    F -->|Valid arguments| G[Establish database connection]
    G --> H[Open SQL input file or read from stdin]
    H --> I[Execute SQL query against database]
    I --> J[Process query results into CSV format]
    J --> K[Write CSV output to stdout/file]
    K --> L[Close database connections and exit]
    F -->|Invalid arguments| M[SystemExit raised]
    M --> L
```

## Examples:
```bash
# Execute SQL query directly
sql2csv --db postgresql://user:pass@localhost/mydb --query "SELECT * FROM users LIMIT 10"

# Execute SQL from file
sql2csv --db mysql://user:pass@localhost/mydb query.sql > output.csv

# Execute SQL from stdin
echo "SELECT COUNT(*) FROM users;" | sql2csv --db sqlite:///mydb.sqlite

# Launch programmatically (equivalent to command-line invocation)
from csvkit.utilities.sql2csv import launch_new_instance
launch_new_instance()
```

