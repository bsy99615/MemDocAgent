# `csvsql.py`

## `csvkit.utilities.csvsql.CSVSQL` · *class*

## Summary:
CSVSQL is a command-line utility that generates SQL statements from CSV files or executes those statements directly on a database, while also supporting SQL query execution and data insertion operations.

## Description:
The CSVSQL class serves as the core implementation for the csvsql command-line tool, enabling users to convert CSV data into SQL schemas and data insertion commands, or execute these operations directly against a database. It provides functionality for generating CREATE TABLE statements, inserting CSV data into databases, executing SQL queries, and managing database transactions. The class extends CSVKitUtility to inherit common CSV processing capabilities while adding database-specific features.

## State:
- input_files (list): List of opened file objects containing CSV data, populated in main()
- connection (sqlalchemy.engine.Connection or None): Database connection object when --db flag is used, set in main()
- table_names (list): List of custom table names provided via --tables flag, parsed in main()
- unique_constraint (list): List of column names to include in UNIQUE constraints, parsed in main()
- args (argparse.Namespace): Parsed command-line arguments from the argument parser
- output_file (file-like object): Output stream for writing results (inherited from CSVKitUtility)

## Lifecycle:
- Creation: Instantiated via command-line interface with optional arguments
- Usage: Called through CSVKitUtility.run() which orchestrates:
  1. Argument parsing and validation in main()
  2. Input file opening via _open_input_file() for each input path
  3. Database connection establishment if --db flag is provided using SQLAlchemy
  4. Main processing via _failsafe_main() method
  5. Resource cleanup in finally block (file closing, connection disposal)
- Destruction: Automatic cleanup of file handles and database connections occurs in the finally block of main()

## Method Map:
```mermaid
graph TD
    A[CSVSQL.run] --> B[CSVSQL.main]
    B --> C[Argument validation and setup]
    C --> D{Connection string provided?}
    D -- Yes --> E[Create SQLAlchemy engine and connection]
    D -- No --> F[Skip DB connection]
    E --> G[Open input files]
    G --> H[Call _failsafe_main]
    H --> I{Has connection?}
    I -- Yes --> J[Process each file with transaction]
    I -- No --> K[Generate CREATE TABLE statements]
    J --> L{Before insert SQL?}
    L -- Yes --> M[Execute before insert queries]
    M --> N[Insert data with to_sql]
    N --> O{After insert SQL?}
    O -- Yes --> P[Execute after insert queries]
    K --> Q[Write CREATE TABLE statement]
    J --> R{Has queries?}
    R -- Yes --> S[Execute queries and output results]
    S --> T[Commit transaction]
    H --> U[Cleanup resources]
    U --> V[Close files and dispose engine]
```

## Raises:
- SystemExit: Raised by argparser.error() for invalid argument combinations or missing required inputs
- ImportError: Raised when database backend is not installed for the specified connection string
- ValueError: May be raised by agate.Table.from_csv() when encountering malformed CSV data

## Example:
```python
# Generate SQL statements for CSV files
csvsql data1.csv data2.csv

# Insert CSV data directly into database
csvsql --db sqlite:///mydb.sqlite --insert data.csv

# Execute SQL queries on database
csvsql --db sqlite:///mydb.sqlite --query "SELECT * FROM mytable"

# Generate SQL with custom table names
csvsql --tables "users,orders" data1.csv data2.csv
```

### `csvkit.utilities.csvsql.CSVSQL.add_arguments` · *method*

## Summary:
Configures command-line argument parsers for CSV to SQL conversion and database operations.

## Description:
This method initializes and configures the argument parser with all available command-line options for the CSVSQL utility. It defines various arguments for specifying input files, SQL dialect generation, database connections, query execution, table creation options, and data insertion behaviors. The method serves as the central configuration point for all CLI options, making it easy to manage and extend the command-line interface.

## Args:
    self: The CSVSQL instance whose argparser attribute is being configured.

## Returns:
    None: This method modifies the instance's argparser in-place and returns nothing.

## Raises:
    None explicitly raised: This method only configures arguments and doesn't raise exceptions itself.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies the argument parser instance)

## Constraints:
    Preconditions: The CSVSQL instance must have an argparser attribute initialized.
    Postconditions: The argparser will contain all defined command-line arguments and help text.

## Side Effects:
    None: This method only configures argument parsing and doesn't perform I/O or external service calls.

## Known Callers:
    This method is called during the initialization phase of the CSVSQL utility when setting up the command-line interface. It's part of the standard CSVKit utility lifecycle where CLI arguments are parsed before processing begins.

## Why This Logic Is Its Own Method:
    This logic is separated into its own method to maintain clean separation of concerns. It allows the CSVSQL class to encapsulate all argument configuration in one place while keeping the main processing logic focused on execution. This approach also makes testing easier and enables reuse of argument definitions across different utility implementations.

### `csvkit.utilities.csvsql.CSVSQL.main` · *method*

## Summary:
Processes CSV input files and generates or executes SQL statements based on command-line arguments, managing database connections and file handles appropriately.

## Description:
This method serves as the primary entry point for the CSVSQL utility, orchestrating the processing of CSV files and handling various SQL generation and execution modes. It performs argument validation, opens input files, establishes database connections when needed, and delegates the actual processing to `_failsafe_main`. The method ensures proper cleanup of resources regardless of success or failure conditions.

## Args:
    self: The CSVSQL instance containing parsed arguments and configuration

## Returns:
    None

## Raises:
    SystemExit: When command-line argument validation fails, triggering parser errors
    ImportError: When required database backend is not installed for the specified connection string

## State Changes:
    Attributes READ: self.args, self.argparser, self.input_files, self.connection, self.table_names, self.unique_constraint
    Attributes WRITTEN: self.input_files, self.connection, self.table_names, self.unique_constraint

## Constraints:
    Preconditions:
    - Command-line arguments must be properly parsed and validated
    - Input paths must be accessible or stdin must be available for piping
    - Database connection string (if specified) must be valid and have required backend installed
    
    Postconditions:
    - All input files are properly opened and stored in self.input_files
    - Database connection is established and stored in self.connection if requested
    - Table names and unique constraint lists are initialized from command-line arguments
    - Resources are cleaned up in finally block regardless of execution outcome

## Side Effects:
    - Opens and closes file handles for input CSV files
    - Establishes and closes database connections using SQLAlchemy
    - May reconfigure stdin encoding when reading from standard input
    - Calls external methods like _open_input_file, _failsafe_main, and SQL-related functions
    - May raise SystemExit for invalid argument combinations
    - May raise ImportError for missing database backends

### `csvkit.utilities.csvsql.CSVSQL._failsafe_main` · *method*

*No documentation generated.*

## `csvkit.utilities.csvsql.launch_new_instance` · *function*

## Summary:
Launches a new instance of the CSVSQL utility to process CSV files and generate or execute SQL statements.

## Description:
This function creates an instance of the CSVSQL class and invokes its run method to execute the command-line utility. It serves as the entry point for the csvsql command-line tool, orchestrating the processing of CSV data according to the specified command-line arguments. The function delegates to CSVKitUtility.run(), which handles argument parsing, file management, and calls the CSVSQL-specific main() method.

## Args:
    None

## Returns:
    None

## Raises:
    Any exceptions raised by CSVSQL.run() or inherited from CSVKitUtility.run(), including:
    - SystemExit: When invalid arguments are provided or required inputs are missing
    - ImportError: When database backend libraries are not installed
    - ValueError: When malformed CSV data is encountered
    - NotImplementedError: If main() method is not properly implemented
    - RequiredHeaderError: If header row requirements are violated

## Constraints:
    Precondition: The command-line environment must be properly initialized with appropriate arguments
    Postcondition: The CSVSQL utility processes input files and produces SQL output or executes database operations

## Side Effects:
    - Reads input CSV files from disk or stdin
    - May write SQL statements to stdout or specified output file
    - May establish database connections and perform database operations
    - May execute SQL queries against databases
    - May modify database tables through insert operations
    - Opens and closes input file handles
    - Applies warning filters for agate library behaviors

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance] --> B[Create CSVSQL instance]
    B --> C[Call CSVSQL.run()]
    C --> D[CSVKitUtility.run() execution]
    D --> E{Check 'f' override}
    E -->|Not overridden| F[Open input file]
    E -->|Overridden| G[Skip file open]
    F --> H[Apply warning filters]
    H --> I[Call CSVSQL.main()]
    I --> J{Connection string provided?}
    J -- Yes --> K[Create SQLAlchemy engine and connection]
    J -- No --> L[Skip DB connection]
    K --> M[Open input files]
    L --> M
    M --> N[Call _failsafe_main()]
    N --> O{Has database connection?}
    O -- Yes --> P[Process with transactions]
    O -- No --> Q[Generate CREATE TABLE statements]
    P --> R{Has before insert queries?}
    R -- Yes --> S[Execute before insert queries]
    S --> T[Insert data with to_sql]
    T --> U{Has after insert queries?}
    U -- Yes --> V[Execute after insert queries]
    Q --> W[Write CREATE TABLE statement]
    P --> X{Has SQL queries?}
    X -- Yes --> Y[Execute queries and output results]
    Y --> Z[Commit transaction]
    N --> AA[Cleanup resources]
    AA --> AB[Close files and dispose engine]
```

## Examples:
```python
# Typical usage from command line
# csvsql data.csv

# With database insertion
# csvsql --db postgresql://user:pass@localhost/db --insert data.csv

# With custom table names
# csvsql --tables "users,orders" data1.csv data2.csv
```

