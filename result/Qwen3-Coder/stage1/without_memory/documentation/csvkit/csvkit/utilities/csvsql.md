# `csvsql.py`

## `csvkit.utilities.csvsql.CSVSQL` · *class*

## Summary:
Generates SQL statements for CSV files or executes those statements directly on a database, and can execute SQL queries on the resulting data.

## Description:
The CSVSQL class is a command-line utility that converts CSV data into SQL operations. It can either generate CREATE TABLE and INSERT statements for databases, or execute these operations directly on a connected database. It also supports executing arbitrary SQL queries on the processed data. This class is part of the csvkit toolkit and extends CSVKitUtility to provide database integration capabilities for CSV processing.

## State:
- input_files: list of opened file objects containing CSV data
- connection: SQLAlchemy database connection object (None if no database specified)
- table_names: list of table names to be created, derived from --tables argument
- unique_constraint: list of column names to include in a UNIQUE constraint
- args: parsed command-line arguments from the argument parser
- output_file: file object for writing output (defaults to stdout)
- reader_kwargs: dictionary of CSV reader configuration parameters
- writer_kwargs: dictionary of CSV writer configuration parameters

## Lifecycle:
Creation: Instantiate with command-line arguments or defaults. The class uses CSVKitUtility's initialization to set up argument parsing.
Usage: Call the main() method which orchestrates the processing workflow:
1. Validate command-line arguments
2. Open input CSV files
3. Establish database connection if needed
4. Process each CSV file to generate SQL or execute operations
5. Handle SQL queries if specified
Usage pattern: Typically called through the command-line interface, but can be instantiated programmatically.
Destruction: Automatically closes all opened input files and database connections in the main() method's finally block.

## Method Map:
```mermaid
graph TD
    A[main] --> B[_failsafe_main]
    B --> C[Open input files]
    B --> D[Process each CSV file]
    D --> E[Parse CSV to agate.Table]
    E --> F[Generate SQL or insert data]
    F --> G{Has DB connection?}
    G -->|Yes| H[to_sql method]
    G -->|No| I[to_sql_create_statement]
    H --> J[Execute before_insert SQL]
    H --> K[Execute table.to_sql]
    H --> L[Execute after_insert SQL]
    I --> M[Write CREATE statement]
    B --> N{Has queries?}
    N -->|Yes| O[Execute queries and output results]
    N -->|No| P[Commit transaction]
```

## Raises:
- SystemExit: Raised by argparser.error() when validation fails
- ImportError: Raised when required database backend is not installed for the connection string
- StopIteration: Raised when CSV file is empty or has no data

## Example:
```python
# Basic usage to generate SQL statements
csvsql = CSVSQL(['file1.csv'])
csvsql.run()

# Usage with database connection to insert data
csvsql = CSVSQL(['--db', 'postgresql://user:pass@localhost/db', '--insert', 'data.csv'])
csvsql.run()

# Usage to execute queries on processed data
csvsql = CSVSQL(['--db', 'sqlite:///test.db', '--query', 'SELECT COUNT(*) FROM table1', 'data.csv'])
csvsql.run()
```

### `csvkit.utilities.csvsql.CSVSQL.add_arguments` · *method*

## Summary
Configures command-line argument parser with all available options for CSV to SQL conversion and database operations.

## Description
This method initializes and configures the argument parser for the CSVSQL utility, defining all available command-line options for processing CSV files and interacting with databases. It sets up arguments for input file specification, SQL dialect selection, database connections, query execution, data insertion, table management, and CSV parsing behavior. The method is part of the CSVSQL class that inherits from CSVKitUtility and follows the standard CLI argument setup pattern.

## Args
This method takes no explicit arguments beyond the implicit `self` parameter.

## Returns
This method returns None.

## Raises
This method does not raise exceptions directly, though argument validation errors may occur during argument parsing if invalid combinations are provided.

## State Changes
- Attributes READ: None
- Attributes WRITTEN: `self.argparser` (modifies the argument parser instance by adding arguments to it)

## Constraints
- This method must be called before the argument parser is used to parse command-line arguments
- All argument definitions are set up in a specific order to maintain logical grouping of related options

## Side Effects
- Modifies the `self.argparser` attribute by adding multiple argument definitions
- No external I/O operations or service calls are performed

### `csvkit.utilities.csvsql.CSVSQL.main` · *method*

## Summary:
Processes CSV input files and generates SQL statements or inserts data into a database based on command-line arguments.

## Description:
This method serves as the primary entry point for the CSVSQL utility, orchestrating the entire workflow from input file handling to database operations or SQL statement generation. It validates command-line arguments, opens input files, establishes database connections when required, and delegates the core processing to `_failsafe_main()`. The method ensures proper resource cleanup regardless of success or failure conditions.

## Args:
    self: The CSVSQL instance containing parsed command-line arguments and configuration.

## Returns:
    None: This method performs side effects and does not return a value.

## Raises:
    SystemExit: Raised by `argparser.error()` when validation fails.
    ImportError: Raised when required database backend is not installed.

## State Changes:
    Attributes READ:
        - self.args: Command-line arguments parsed by argparse
        - self.args.input_paths: List of input file paths
        - self.args.connection_string: Database connection string
        - self.args.table_names: Comma-separated table names
        - self.args.unique_constraint: Comma-separated unique constraint columns
        - self.args.queries: SQL queries to execute
        - self.args.dialect: SQL dialect to use for statement generation
        - self.args.insert: Flag indicating whether to insert data
        - self.args.no_create: Flag indicating whether to skip table creation
        - self.args.create_if_not_exists: Flag indicating whether to create tables if they don't exist
        - self.args.overwrite: Flag indicating whether to overwrite existing tables
        - self.args.before_insert: SQL queries to run before insertion
        - self.args.after_insert: SQL queries to run after insertion
        - self.args.chunk_size: Size of chunks for batch insertion
        - self.args.sniff_limit: Limit for CSV sniffing
        - self.args.skip_lines: Number of initial lines to skip
        - self.args.columns: Column selection specification
        - self.args.not_columns: Column exclusion specification
        - self.args.no_header_row: Flag indicating no header row in input
        - self.args.no_constraints: Flag indicating whether to include constraints
        - self.args.prefix: Table name prefixes
        - self.args.db_schema: Database schema name
        - self.args.zero_based: Flag for zero-based column indexing
        - self.args.verbose: Flag for verbose output
        - self.args.encoding: Input file encoding
        - self.args.locale: Locale for number formatting
        - self.args.date_format: Date format string
        - self.args.datetime_format: Datetime format string
        - self.args.no_inference: Flag for type inference
        - self.args.null_values: Additional null value specifications
        - self.args.blanks: Flag for blank value handling
        - self.args.skipinitialspace: Flag for skipping initial space
        - self.args.escapechar: Escape character for CSV
        - self.args.doublequote: Flag for double quote handling
        - self.args.quoting: Quoting style for CSV
        - self.args.quotechar: Quote character for CSV
        - self.args.delimiter: Delimiter character for CSV
        - self.args.tabs: Flag for tab-delimited input
        - self.args.field_size_limit: Maximum field size limit
        - self.args.line_numbers: Flag for line number inclusion
        - self.args.version: Flag for version display

    Attributes WRITTEN:
        - self.input_files: List of opened input file handles
        - self.connection: Database connection object
        - self.table_names: Processed table names from command-line argument
        - self.unique_constraint: Processed unique constraint columns from command-line argument

## Constraints:
    Preconditions:
        - Command-line arguments must be properly parsed
        - Input files must be accessible or stdin must be available for piped input
        - Valid database connection string must be provided when using database operations
        - Appropriate combinations of flags must be used (e.g., --insert requires --db or --query)

    Postconditions:
        - All input files are properly closed
        - Database connections are properly disposed
        - SQL statements are written to output or data is inserted into database
        - Error messages are displayed appropriately for invalid argument combinations

## Side Effects:
    - Reads from input files or stdin
    - Writes SQL statements to output file or stdout
    - Establishes database connections and executes database operations
    - May execute SQL queries from command-line arguments
    - May perform file I/O operations for reading input files
    - May perform network I/O when connecting to databases
    - May raise SystemExit for invalid command-line arguments

### `csvkit.utilities.csvsql.CSVSQL._failsafe_main` · *method*

*No documentation generated.*

## `csvkit.utilities.csvsql.launch_new_instance` · *function*

*No documentation generated.*

