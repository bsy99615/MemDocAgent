# `csvsql.py`

## `csvkit.utilities.csvsql.CSVSQL` · *class*

## Summary:
Generates SQL statements for CSV files or executes those statements directly on a database, and can execute SQL queries on the resulting data.

## Description:
The CSVSQL class is a command-line utility that transforms CSV data into SQL operations. It can either generate SQL CREATE TABLE and INSERT statements for the CSV data, or execute these statements directly against a database. Additionally, it supports executing arbitrary SQL queries on the processed data and outputting results as CSV.

This class extends CSVKitUtility and provides functionality for:
- Converting CSV files to SQL schema and data insertion commands
- Direct database operations using SQLAlchemy connections
- Executing SQL queries on processed data
- Configurable table naming, constraints, and insertion behaviors

## State:
- input_files (list[file-like objects]): List of opened input file handles for CSV files
- connection (sqlalchemy.engine.base.Connection or None): Database connection object when --db is specified, otherwise None
- table_names (list[str]): Names for tables to be created, parsed from --tables argument
- unique_constraint (list[str]): Column names to include in a UNIQUE constraint, parsed from --unique-constraint argument
- args (argparse.Namespace): Parsed command-line arguments from the argument parser
- argparser (argparse.ArgumentParser): Argument parser instance for command-line interface
- output_file (file-like object): Output destination (inherited from CSVKitUtility, defaults to sys.stdout)
- reader_kwargs (dict): Configuration parameters for CSV readers (inherited from CSVKitUtility)
- writer_kwargs (dict): Configuration parameters for CSV writers (inherited from CSVKitUtility)

## Lifecycle:
- Creation: Instantiated by the command-line interface with parsed arguments, inheriting from CSVKitUtility
- Usage: Called via the run() method inherited from CSVKitUtility, which internally calls main() method
- Destruction: Automatically closes input files and database connections in the main() method's finally block

## Method Map:
```mermaid
graph TD
    A[CSVSQL.run] --> B[CSVSQL.main]
    B --> C[CSVSQL._failsafe_main]
    C --> D[CSVSQL._open_input_file]
    D --> E[agate.Table.from_csv]
    E --> F[agate.Table.to_sql_create_statement]
    F --> G[CSVSQL.output_file.write]
    E --> H[agate.Table.to_sql]
    H --> I[connection.exec_driver_sql]
    I --> J[CSVSQL.output_file.write]
```

## Raises:
- SystemExit: Raised by argparser.error() when validation fails due to conflicting arguments
- ImportError: Raised when required database backend is not installed for the connection string
- StopIteration: Raised by agate.Table.from_csv when encountering empty files

## Example:
```python
# Generate SQL statements for CSV files
csvsql input.csv

# Execute SQL directly on a database
csvsql --db sqlite:///example.db input.csv --insert

# Execute SQL queries on processed data
csvsql --db sqlite:///example.db input.csv --query "SELECT COUNT(*) FROM stdin"

# Insert data with constraints and custom table names
csvsql --db postgresql://user:pass@localhost/db input.csv --insert --tables my_table --no-constraints
```

### `csvkit.utilities.csvsql.CSVSQL.add_arguments` · *method*

## Summary:
Configures command-line arguments for CSV to SQL conversion and database operations.

## Description:
This method sets up all available command-line options for the CSVSQL utility, defining how users can interact with the tool to convert CSV files to SQL statements or execute them directly against a database. It registers arguments with the argument parser for file input, SQL dialect selection, database connections, query execution, data insertion, table creation, and various operational modes.

The method is part of the standard CSVKit utility pattern where subclasses implement `add_arguments()` to define their specific command-line interface, and is called automatically during the utility initialization process.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies by adding arguments to it)

## Constraints:
    Preconditions: The method assumes self.argparser exists and is an argparse.ArgumentParser instance
    Postconditions: The self.argparser instance contains all registered command-line arguments for CSVSQL functionality

## Side Effects:
    None

### `csvkit.utilities.csvsql.CSVSQL.main` · *method*

## Summary:
Main execution entry point for the CSVSQL utility that processes CSV files and generates or executes SQL statements.

## Description:
This method serves as the primary orchestration point for the CSVSQL utility, managing the complete workflow from argument parsing to file handling, database connection establishment, and execution of the core processing logic. It validates command-line arguments, opens input files, establishes database connections when needed, and delegates to the internal processing method while ensuring proper resource cleanup.

The method handles various command-line options including database connections, table naming, constraints, and SQL query execution. It implements comprehensive error checking for mutually exclusive options and required parameter combinations, raising ArgumentParser errors when validation fails.

## Args:
    None - This is a method of the CSVSQL class and operates on instance attributes

## Returns:
    None - This method performs side effects rather than returning a value

## Raises:
    SystemExit - Raised by argparser.error() when command-line argument validation fails
    ImportError - Raised when required database backend is not installed for the specified connection string

## State Changes:
    Attributes READ: self.args, self.argparser, self.input_files, self.connection, self.table_names, self.unique_constraint
    Attributes WRITTEN: self.input_files, self.connection, self.table_names, self.unique_constraint

## Constraints:
    Preconditions:
    - Command-line arguments must be properly parsed and available in self.args
    - When reading from stdin, input_paths should not be ['-'] without piped data
    - Required argument combinations must be satisfied (e.g., --insert requires --db or --query)
    - Mutually exclusive options must not be specified simultaneously
    
    Postconditions:
    - All input files are properly closed
    - Database connections are properly closed and disposed
    - The internal _failsafe_main method is called to process the actual work
    - Resource cleanup occurs regardless of success or failure

## Side Effects:
    - Reads from stdin or files specified in self.args.input_paths
    - Opens and closes file handles from self.input_files
    - Establishes database connections via SQLAlchemy when self.args.connection_string is provided
    - Calls argparser.error() to terminate execution on invalid argument combinations
    - May raise ImportError for missing database backends
    - Invokes the internal _failsafe_main method for core processing
    - Performs cleanup operations in finally blocks to ensure resource release

### `csvkit.utilities.csvsql.CSVSQL._failsafe_main` · *method*

## Summary:
Processes CSV input files by either inserting data into a database or generating SQL CREATE statements, handling database transactions and query execution.

## Description:
This method serves as the core processing routine for the CSVSQL utility. It iterates through input CSV files, reads them using agate, and either executes SQL INSERT operations against a connected database or generates CREATE TABLE statements. The method handles database transactions, manages table naming conventions, and supports additional SQL operations before/after insertions and custom queries.

The method is designed to be called from the main() method and handles error recovery gracefully, ensuring proper cleanup of resources even when errors occur.

## Args:
    None - This is a method of the CSVSQL class and operates on instance attributes

## Returns:
    None - This method performs side effects rather than returning a value

## Raises:
    None - Exceptions are handled internally within the method

## State Changes:
    Attributes READ: self.connection, self.input_files, self.table_names, self.args, self.unique_constraint, self.output_file, self.reader_kwargs
    Attributes WRITTEN: None - This method doesn't modify instance attributes directly

## Constraints:
    Preconditions:
    - self.input_files must be populated with file objects
    - self.connection must be properly initialized if database operations are intended
    - self.args must contain valid configuration parameters
    - Table names must be available in self.table_names or derivable from input files
    
    Postconditions:
    - Input files are closed properly
    - Database connection is closed properly
    - SQL statements are written to output_file when appropriate
    - Database transactions are committed when appropriate

## Side Effects:
    - Opens and closes input files from self.input_files
    - Creates database connections and transactions when self.connection is set
    - Writes SQL statements to self.output_file
    - Executes SQL queries against the database connection
    - May read from filesystem when processing query files
    - May perform database insert operations

## `csvkit.utilities.csvsql.launch_new_instance` · *function*

## Summary:
Creates and executes a CSVSQL utility instance to process CSV files and generate or execute SQL statements.

## Description:
The `launch_new_instance` function serves as a factory and execution entry point for the CSVSQL command-line utility. It instantiates a CSVSQL class object and invokes its run() method to process CSV data according to command-line arguments. This function abstracts away the instantiation and execution details, providing a clean interface for launching the CSVSQL utility.

This function is typically used as the main entry point for the csvsql command-line tool, where it creates a properly configured CSVSQL instance and executes it with the appropriate command-line arguments. The function leverages the CSVKitUtility base class infrastructure for argument parsing, file handling, and CSV processing.

## Args:
    None: This function takes no parameters.

## Returns:
    None: This function does not return a value. It executes the CSVSQL utility and handles its lifecycle internally.

## Raises:
    SystemExit: May be raised by the underlying CSVSQL.run() method when command-line argument validation fails.
    ImportError: May be raised by the underlying CSVSQL.main() method when required database backends are not installed.
    Various exceptions: May propagate from underlying CSV processing or database operations.

## Constraints:
    Preconditions:
        - Command-line arguments must be available in sys.argv for argument parsing
        - The CSVSQL class must be properly imported and available
        - The CSVKitUtility base class must be properly initialized
        
    Postconditions:
        - A CSVSQL instance is created and executed
        - Command-line arguments are parsed and processed
        - CSV files are read and processed according to specified options
        - SQL statements are generated or executed as appropriate

## Side Effects:
    - Reads command-line arguments from sys.argv
    - May read CSV input files from disk or stdin
    - May establish database connections when --db flag is specified
    - May write SQL output to stdout or files
    - May write error messages to stderr
    - May create temporary files during processing

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance] --> B[CSVSQL()]
    B --> C[utility.run()]
    C --> D[CSVSQL.run()]
    D --> E[CSVSQL.main()]
    E --> F[CSVSQL._failsafe_main()]
    F --> G[Input file handling]
    G --> H[Database connection setup]
    H --> I[SQL generation or execution]
    I --> J[Output generation]
    J --> K[Resource cleanup]
```

## Examples:
```python
# Typical usage from command line:
# csvsql input.csv --db sqlite:///mydb.sqlite3 --insert

# Programmatic usage:
from csvkit.utilities.csvsql import launch_new_instance
launch_new_instance()
```

