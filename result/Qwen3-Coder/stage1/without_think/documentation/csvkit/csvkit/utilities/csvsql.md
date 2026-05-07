# `csvsql.py`

## `csvkit.utilities.csvsql.CSVSQL` · *class*

## Summary:
Generates SQL statements from CSV files or executes those statements directly on a database, with support for querying and inserting data.

## Description:
The CSVSQL class serves as a command-line utility for converting CSV data into SQL operations. It can either generate CREATE TABLE and INSERT statements for database insertion, or execute these statements directly against a database connection. The class supports various options for controlling table creation, data insertion behavior, and SQL query execution.

This class is designed to be instantiated by the csvkit command-line interface and handles the complete workflow of reading CSV files, processing them according to user-specified options, and either outputting SQL statements or executing them against a database. It inherits from CSVKitUtility, which provides base CLI functionality.

## State:
- input_files: list of opened file handles for CSV input (populated in main())
- connection: SQLAlchemy database connection object (None if not connected, managed in main())
- table_names: list of table names to be created (parsed from --tables argument)
- unique_constraint: list of column names to include in a UNIQUE constraint (parsed from --unique-constraint argument)
- args: parsed command-line arguments from argparse (inherited from CSVKitUtility)
- argparser: argument parser instance (inherited from CSVKitUtility)
- output_file: file handle for output (inherited from CSVKitUtility, typically stdout)

## Lifecycle:
- Creation: Instantiated automatically by the csvkit CLI framework with command-line arguments
- Usage: Called via main() method which validates arguments, opens files, establishes database connections, and processes CSV data
- Destruction: Automatically closes all input files and database connections in the finally block of main()

## Method Map:
```mermaid
graph TD
    A[main] --> B[validate_arguments]
    A --> C[open_input_files]
    A --> D[establish_database_connection]
    A --> E[_failsafe_main]
    E --> F[process_each_file]
    F --> G[read_csv_with_agate]
    F --> H[generate_sql_or_insert]
    H --> I[to_sql_create_statement] 
    H --> J[to_sql]
    E --> K[execute_queries_if_requested]
    K --> L[exec_driver_sql]
```

## Raises:
- SystemExit: Raised by argparser.error() when validation fails due to conflicting arguments or missing required options
- ImportError: Raised when required database backend is not installed for the specified connection string
- Exception: Propagated from underlying CSV reading operations (StopIteration) or database operations

## Example:
```python
# Typical usage would be via command line:
# csvsql --db sqlite:///mydb.sqlite myfile.csv --insert
# csvsql --dialect postgresql myfile.csv
# csvsql --db postgresql://user:pass@localhost/db --insert myfile.csv

# Programmatic instantiation (via CLI framework):
utility = CSVSQL(['myfile.csv'])
utility.run()
```

### `csvkit.utilities.csvsql.CSVSQL.add_arguments` · *method*

*No documentation generated.*

### `csvkit.utilities.csvsql.CSVSQL.main` · *method*

## Summary:
Validates command-line arguments, sets up input files and database connections, and orchestrates the conversion of CSV files to SQL operations.

## Description:
The main method serves as the primary entry point for the CSVSQL utility, responsible for validating user input, establishing database connections when needed, and coordinating the processing of CSV files into SQL operations. It performs extensive argument validation to ensure proper usage of command-line options, handles input file management, and delegates the core processing to the `_failsafe_main` method.

This method is designed to be robust against various error conditions and ensures proper resource cleanup regardless of success or failure. It handles both the generation of SQL CREATE statements for database schemas and the direct insertion of CSV data into databases, making it the central coordination point for all CSV-to-SQL operations.

## Args:
    None (uses self.args from the CSVSQL instance)

## Returns:
    None

## Raises:
    SystemExit: When command-line argument validation fails, causing the program to exit with an error message
    ImportError: When required database backend libraries are missing for the specified connection string

## State Changes:
    Attributes READ: self.args, self.argparser, self.input_files, self.connection, self.table_names, self.unique_constraint
    Attributes WRITTEN: self.input_files, self.connection, self.table_names, self.unique_constraint

## Constraints:
    Preconditions:
    - Command-line arguments must be properly parsed and available in self.args
    - Input paths must be valid or stdin must be properly configured
    - Database connection strings must be compatible with SQLAlchemy
    - Required database backend libraries must be installed for specified connection strings
    
    Postconditions:
    - All input files are properly opened and tracked in self.input_files
    - Database connection is established if connection_string is provided
    - All resources are properly cleaned up (files closed, connections disposed)
    - Processing is delegated to _failsafe_main method

## Side Effects:
    - Reads input files from specified paths or stdin
    - Establishes database connections via SQLAlchemy when connection_string is provided
    - Writes SQL statements to output file when no database connection is specified
    - Executes SQL queries against database connections when --query is specified
    - May read additional query files from disk when --query specifies file paths
    - Closes all input files and disposes database connections upon completion
    - May raise SystemExit for invalid argument combinations
    - May raise ImportError for missing database backend libraries

### `csvkit.utilities.csvsql.CSVSQL._failsafe_main` · *method*

## Summary:
Processes CSV input files and converts them to SQL operations, either inserting data into a database or generating CREATE statements, while managing database transactions and executing additional SQL queries.

## Description:
This method serves as the core processing engine for the CSVSQL utility, handling the conversion of one or more CSV files into SQL operations. It manages database connections, processes input files sequentially, determines appropriate table names, reads CSV data using agate, and either executes SQL INSERT operations against a database connection or generates CREATE TABLE statements for SQL dialects. The method also supports executing additional SQL queries before/after insert operations and handles complex transaction management.

The method is designed to be "failsafe" by gracefully handling empty files (StopIteration exceptions) and ensuring proper cleanup of resources even when errors occur. It processes all input files in sequence, continuing past individual file errors rather than aborting the entire process.

## Args:
    None

## Returns:
    None

## Raises:
    None explicitly raised - though underlying operations may raise exceptions from agate, SQLAlchemy, or file I/O operations

## State Changes:
    Attributes READ: self.connection, self.input_files, self.table_names, self.args, self.unique_constraint, self.output_file, self.reader_kwargs, self.writer_kwargs
    Attributes WRITTEN: None (modifies state through database operations and output writing)

## Constraints:
    Preconditions: 
    - self.input_files must be populated with open file handles
    - self.connection may be None or a valid SQLAlchemy connection
    - self.args must contain parsed command-line arguments
    - Table names should be available in self.table_names or will be auto-generated
    
    Postconditions:
    - All input files are processed
    - Database transactions are committed (if applicable)
    - Output is written to self.output_file (either SQL statements or query results)
    - Resources are properly closed

## Side Effects:
    - Opens and closes input files from self.input_files
    - May establish database connections via SQLAlchemy
    - Writes SQL statements to self.output_file
    - Executes SQL queries against database connections
    - May read additional query files from disk when self.args.queries is specified
    - Commits database transactions when applicable
    - Handles StopIteration exceptions gracefully by continuing to next file

## `csvkit.utilities.csvsql.launch_new_instance` · *function*

## Summary:
Creates and executes a new instance of the CSVSQL command-line utility for converting CSV files to SQL operations.

## Description:
This function serves as the entry point for launching the CSVSQL command-line utility. It instantiates a CSVSQL object and invokes its run method to process command-line arguments and perform CSV-to-SQL conversions. The function follows the standard CSVKit framework pattern where utilities are launched through a dedicated initialization and execution sequence.

The CSVSQL utility can either generate SQL CREATE TABLE and INSERT statements for database insertion or execute these statements directly against a database connection. This function is typically called by the csvkit command-line framework when the 'csvsql' command is executed, providing a consistent interface for initializing and running the CSV-to-SQL conversion utility.

## Args:
    None

## Returns:
    None

## Raises:
    SystemExit: Raised by CSVSQL's argument parser when command-line argument validation fails
    ImportError: Raised when required database backend libraries are missing for the specified connection string
    Exception: Propagated from underlying CSV reading operations or database operations

## Constraints:
    Preconditions:
    - The csvkit command-line framework must be properly initialized
    - Command-line arguments must be available for parsing (typically via sys.argv)
    - Input file paths (if specified) must be accessible
    - Database connection strings (if specified) must be compatible with SQLAlchemy
    
    Postconditions:
    - A CSVSQL instance is created and executed
    - Command-line arguments are parsed and processed
    - CSV data is converted to SQL operations or executed against a database
    - Appropriate output is generated to stdout or written to a database

## Side Effects:
    - Reads from input file(s) or stdin when processing CSV data
    - Writes SQL statements to output file or stdout when no database connection is specified
    - Establishes database connections via SQLAlchemy when connection_string is provided
    - Executes SQL queries against database connections when --query is specified
    - May read additional query files from disk when --query specifies file paths
    - Closes all input files and disposes database connections upon completion

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[CSVSQL().__init__()]
    B --> C[utility.run()]
    C --> D[CSVKitUtility.run()]
    D --> E[Parse command-line arguments]
    E --> F{Database connection specified?}
    F -->|Yes| G[Establish database connection]
    F -->|No| H[Skip database connection]
    G --> I[Open input files]
    H --> I
    I --> J[Validate arguments]
    J --> K{Query mode requested?}
    K -->|Yes| L[Execute SQL queries]
    K -->|No| M[Generate SQL statements]
    M --> N[Write SQL to output]
    L --> O[Execute queries against database]
    O --> P[End execution]
    N --> P
```

## Examples:
```bash
# Generate SQL statements for database insertion
csvsql data.csv

# Execute SQL statements directly against a database
csvsql --db sqlite:///mydb.sqlite data.csv --insert

# Generate SQL with specific table names
csvsql --tables mytable data.csv

# Query a database with SQL statements
csvsql --db postgresql://user:pass@localhost/db --query "SELECT * FROM mytable" data.csv

# Specify a dialect for SQL generation
csvsql --dialect postgresql data.csv
```

