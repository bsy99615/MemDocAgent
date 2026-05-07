# `csvsql.py`

## `csvkit.utilities.csvsql.CSVSQL` · *class*

## Summary:
Generates SQL statements for CSV files or executes those statements directly on a database, and can execute SQL queries.

## Description:
The CSVSQL class is a command-line utility that bridges CSV data processing with SQL database operations. It allows users to convert CSV files into SQL CREATE TABLE statements, insert CSV data into database tables, or execute SQL queries directly on databases. This utility is particularly useful for data migration, database schema generation, and executing analytical queries on CSV datasets.

The class extends CSVKitUtility and provides functionality for:
- Generating SQL DDL statements from CSV files
- Directly inserting CSV data into database tables
- Executing SQL queries on databases
- Configurable table naming, constraints, and insertion options

Key operational modes:
1. Schema generation mode: Creates SQL CREATE TABLE statements for CSV files
2. Database insertion mode: Inserts CSV data directly into database tables
3. Query execution mode: Executes SQL queries on existing databases

## State:
- `input_files`: List of opened input file handles for CSV files
- `connection`: SQLAlchemy database connection object (when --db flag is used)
- `table_names`: List of table names to be created, parsed from --tables argument
- `unique_constraint`: List of column names to include in UNIQUE constraint, parsed from --unique-constraint argument
- Inherits all state from CSVKitUtility parent class including argparser, args, output_file, reader_kwargs, writer_kwargs

## Lifecycle:
Creation: Instantiate with command-line arguments. The constructor initializes the argument parser and sets up standard CSV processing capabilities through CSVKitUtility parent class.

Usage: Call `run()` method which:
1. Validates command-line arguments through argument validation logic
2. Opens input CSV files using `_open_input_file()` method
3. Establishes database connection if --db flag is specified using SQLAlchemy
4. Processes each CSV file through `_failsafe_main()` method
5. Handles SQL query execution if --query flag is specified
6. Commits transactions and closes resources

Destruction: Automatic cleanup occurs through context managers and file closing in the run() method.

## Method Map:
```mermaid
graph TD
    A[run()] --> B[validate_args()]
    A --> C[open_input_files()]
    A --> D[establish_db_connection()]
    A --> E[_failsafe_main()]
    E --> F[for each input_file]
    F --> G[get_table_name()]
    G --> H[from_csv()]
    H --> I{has_connection?}
    I -->|Yes| J[to_sql()]
    I -->|No| K[to_sql_create_statement()]
    F --> L{has_queries?}
    L -->|Yes| M[execute_queries()]
    L -->|No| N[continue]
    E --> O[commit_transaction()]
    A --> P[close_resources()]
```

## Raises:
- SystemExit: Raised by argparser.error() for invalid argument combinations
- ImportError: Raised when required database backend is not installed for connection string
- UnicodeDecodeError: Propagated from file operations when encoding issues occur
- sqlalchemy.exc.*: Various SQLAlchemy exceptions when database operations fail

## Example:
```python
# Generate SQL statements for CSV files
csvsql file1.csv file2.csv

# Insert CSV data into database table
csvsql --db sqlite:///mydb.sqlite --insert file1.csv

# Execute SQL queries on database
csvsql --db postgresql://user:pass@localhost/mydb --query "SELECT * FROM mytable"

# Generate SQL with custom table names and constraints
csvsql --tables "users,orders" --no-constraints file1.csv

# Insert with additional options
csvsql --db mysql://user:pass@localhost/mydb --insert --overwrite --prefix "OR REPLACE" file1.csv

# Execute queries with file input
csvsql --db sqlite:///mydb.sqlite --query queries.sql
```

### `csvkit.utilities.csvsql.CSVSQL.add_arguments` · *method*

## Summary:
Configures command-line argument parser with comprehensive options for CSV to SQL conversion and database operations.

## Description:
This method initializes the argument parser with command-line options that control CSV file processing, SQL dialect generation, database connectivity, query execution, and table management. It provides a complete interface for converting CSV data to SQL statements or executing SQL operations directly on databases.

The method organizes arguments into logical groups:
- Input specification: controlling which CSV files to process
- SQL generation: specifying SQL dialect and schema options  
- Database connectivity: configuring database connections and insertion behavior
- Query execution: running SQL queries on databases
- Table management: controlling table creation, modification, and constraints
- CSV processing: configuring CSV parsing behavior

## Args:
    self: The CSVSQL instance whose argparser is being configured.

## Returns:
    None: This method modifies the instance's argparser in-place and returns nothing.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies the argument parser instance)

## Constraints:
    Preconditions: The method assumes self.argparser exists and is a proper ArgumentParser instance.
    Postconditions: The argparser instance will contain all defined command-line arguments for CSVSQL functionality.

## Side Effects:
    None: This method only configures the argument parser and doesn't perform I/O or external service calls.

### `csvkit.utilities.csvsql.CSVSQL.main` · *method*

## Summary:
Processes command-line arguments, opens input files, establishes database connections, and orchestrates the main workflow for generating or executing SQL statements from CSV data.

## Description:
This method serves as the entry point for the csvsql utility, handling argument validation, file management, database connection setup, and coordinating the execution flow. It performs comprehensive validation of command-line options to ensure they are used appropriately and sets up the necessary resources before delegating to the core processing logic in `_failsafe_main`.

The method manages the complete lifecycle of input files and database connections, ensuring proper cleanup regardless of success or failure conditions. It also handles special cases like stdin input validation and automatic connection string generation for query execution.

## Args:
    self: The CSVSQL instance containing parsed arguments and utility state

## Returns:
    None: This method doesn't return a value but may raise exceptions during validation or execution

## Raises:
    SystemExit: Raised by argparser.error() when command-line argument validation fails
    ImportError: Raised when required database backend libraries are missing for the specified connection string

## State Changes:
    Attributes READ: self.args, self.argparser, self.input_files, self.connection, self.table_names, self.unique_constraint
    Attributes WRITTEN: self.input_files, self.connection, self.table_names, self.unique_constraint

## Constraints:
    Preconditions:
    - self.args must contain parsed command-line arguments
    - self.argparser must be initialized from the parent class
    - Input paths in self.args.input_paths must be valid or '-' for stdin
    
    Postconditions:
    - self.input_files contains opened file handles for all input paths
    - self.connection is established if a connection string was provided
    - All input files are properly closed after execution
    - Database connection is properly disposed after execution

## Side Effects:
    - Validates command-line arguments and exits with error messages if invalid combinations are detected
    - Opens and manages file handles for input CSV files
    - Establishes database connections using SQLAlchemy
    - Calls _failsafe_main() to perform the core CSV-to-SQL conversion or execution logic
    - Ensures proper cleanup of file handles and database connections through try/finally blocks
    - May modify self.args.connection_string and self.args.insert when --queries is specified

### `csvkit.utilities.csvsql.CSVSQL._failsafe_main` · *method*

## Summary:
Processes CSV input files and converts them to SQL operations, either inserting data into a database or generating CREATE TABLE statements.

## Description:
This method serves as the core processing engine for the CSVSQL utility. It iterates through input files, reads CSV data using agate, and either executes SQL INSERT operations against a connected database or generates CREATE TABLE statements for database schema creation. The method handles table naming logic, data type inference, and manages database transactions appropriately.

The method is designed to be called from the main() method after all initialization is complete, and it encapsulates the complete workflow for CSV-to-SQL conversion while providing error handling and resource management.

## Args:
    None - This is a method that operates on self and uses instance attributes

## Returns:
    None - This method performs I/O operations and modifies object state but does not return a value

## Raises:
    Exception - Various exceptions may be raised during database operations, file I/O, or SQL execution that would propagate up to the caller. Note that StopIteration is caught internally and does not propagate.

## State Changes:
    Attributes READ:
    - self.connection: Database connection object used for SQL operations
    - self.input_files: List of opened input file handles
    - self.table_names: List of table names to assign to processed files
    - self.args: Command-line arguments parsed by argparse
    - self.unique_constraint: List of column names for unique constraint
    - self.reader_kwargs: Keyword arguments for CSV reader configuration
    - self.output_file: Output file handle for writing SQL statements
    - self.writer_kwargs: Keyword arguments for CSV writer configuration

    Attributes WRITTEN:
    - self.table_names: Modified by popping elements during table name assignment
    - transaction: Local variable managing database transaction state (not an attribute)

## Constraints:
    Preconditions:
    - self.input_files must be populated with valid file handles
    - self.args must be properly initialized through argparse parsing
    - If using database operations, self.connection must be established
    - Table names in self.table_names should be sufficient for all input files, though fallback logic exists

    Postconditions:
    - All input files are closed properly
    - Database connections are closed and disposed
    - Transaction is committed if database operations were performed
    - Appropriate SQL operations are executed or written to output

## Side Effects:
    - Database operations: Executes SQL INSERT/CREATE statements when a database connection is present
    - File I/O: Reads from input CSV files and writes SQL statements to output file
    - Resource management: Opens/closes file handles and manages database connections
    - Transaction management: Begins and commits database transactions
    - Query execution: Executes additional SQL queries specified by --query flag

## `csvkit.utilities.csvsql.launch_new_instance` · *function*

## Summary:
Creates and executes a new CSVSQL utility instance to generate SQL statements from CSV files or execute SQL operations on databases.

## Description:
This function serves as the primary entry point for launching the CSVSQL command-line utility. It instantiates a CSVSQL object and invokes its run() method to process command-line arguments and execute SQL generation or database operations on CSV data. The function follows the standard csvkit pattern where command-line utilities are instantiated and executed through a dedicated launch function.

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
    SystemExit: Raised by CSVSQL.run() when argument validation fails or when the utility encounters fatal errors during execution
    ImportError: Raised when required database backend is not installed for connection string
    UnicodeDecodeError: Potentially raised during CSV reading if encoding issues occur (handled by parent class)
    sqlalchemy.exc.*: Various SQLAlchemy exceptions when database operations fail

## Constraints:
    Preconditions:
    - Command-line arguments must be available via sys.argv for parsing
    - Standard input/output streams must be accessible
    - Required CSV processing dependencies must be available
    - Input files (if specified) must be readable
    - Database connection strings (if specified) must be valid and accessible
    
    Postconditions:
    - A CSVSQL utility instance is created and executed
    - Either SQL statements are generated or database operations are performed
    - All temporary resources are properly cleaned up

## Side Effects:
    - Reads from standard input or specified input files (via CSVKitUtility's input_file handling)
    - Writes to standard output or specified output files (via CSVKitUtility's output_file handling)
    - Processes command-line arguments from sys.argv through CSVKitUtility's argument parser
    - May establish database connections when --db flag is specified
    - May read from files specified via --query flag when executing SQL queries
    - May modify database state when --insert flag is used with database connections

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[Create CSVSQL() instance]
    B --> C[Call utility.run()]
    C --> D{Input file handling}
    D -->|File specified| E[Open input file]
    D -->|No file| F[Use stdin]
    E --> G[Parse command-line arguments]
    F --> G
    G --> H{Validation checks}
    H -->|Invalid args| I[Display error and exit]
    H -->|Valid args| J[Process CSV data]
    J --> K{Database connection requested?}
    K -->|Yes| L[Establish database connection]
    K -->|No| M[Skip database connection]
    L --> N[Process CSV to SQL generation]
    M --> N
    N --> O{SQL query requested?}
    O -->|Yes| P[Execute SQL queries]
    O -->|No| Q[Generate SQL statements]
    P --> R[Write query results to output]
    Q --> R
    R --> S[Cleanup and exit]
```

