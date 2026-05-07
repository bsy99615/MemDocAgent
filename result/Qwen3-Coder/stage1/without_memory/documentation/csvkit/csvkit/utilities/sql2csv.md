# `sql2csv.py`

## `csvkit.utilities.sql2csv.SQL2CSV` · *class*

## Summary:
SQL2CSV is a command-line utility that executes SQL queries against databases and outputs the results to CSV format.

## Description:
This class implements a CSVKit utility for executing SQL queries on database systems and converting the results into CSV format. It serves as a bridge between database systems and CSV output, allowing users to run SQL queries and export tabular data to CSV files. The class is designed to be instantiated by the CSVKit framework and handles command-line argument parsing, database connection management, and CSV output generation.

## State:
- `description` (str): A descriptive string explaining the utility's purpose
- `override_flags` (list): List of flags that this utility overrides from the base CSVKitUtility
- `args` (argparse.Namespace): Parsed command-line arguments
- `output_file`: File object for writing CSV output
- `input_file`: File object for reading SQL query input
- `writer_kwargs`: Keyword arguments for configuring CSV writer behavior

## Lifecycle:
Creation: Instances are created automatically by the CSVKit framework when the command-line utility is invoked. The constructor initializes argument parsing and sets up the command-line interface.

Usage: The utility follows the standard CSVKit pattern:
1. Arguments are parsed via `add_arguments()` and `__init__()`
2. The `run()` method orchestrates execution by calling `main()`
3. In `main()`, database connection is established, SQL query is executed, and results are written to CSV

Destruction: Cleanup occurs automatically when the utility completes execution, closing database connections and disposing of engine resources.

## Method Map:
```mermaid
graph TD
    A[SQL2CSV.__init__] --> B[SQL2CSV.add_arguments]
    B --> C[SQL2CSV.run]
    C --> D[SQL2CSV.main]
    D --> E[create_engine]
    E --> F[engine.connect]
    F --> G[connection.exec_driver_sql]
    G --> H[agate.csv.writer]
    H --> I[output.writerow]
    I --> J[connection.close]
    J --> K[engine.dispose]
```

## Raises:
- `ImportError`: Raised when the required database backend is not installed for the specified connection string
- `argparse.ArgumentError`: Raised when required input is missing (when `additional_input_expected()` returns True and no query is provided)
- Various exceptions from database drivers when connecting to or querying the database

## Example:
```python
# Typical usage from command line:
# sql2csv --db postgresql://user:pass@localhost/dbname query.sql > output.csv

# Or with inline query:
# sql2csv --db sqlite:///example.db --query "SELECT * FROM users" > output.csv

# Programmatic usage would involve:
# 1. Creating an instance with appropriate arguments
# 2. Calling the run() method
# 3. The utility handles database connection, query execution, and CSV output
```

### `csvkit.utilities.sql2csv.SQL2CSV.add_arguments` · *method*

## Summary:
Configures command-line arguments for SQL to CSV conversion utility.

## Description:
Adds command-line argument definitions to the utility's argument parser for configuring database connections, input sources, query execution, and output formatting options. This method is called during the initialization phase of the SQL2CSV utility to define all available command-line options.

## Args:
    self: The SQL2CSV instance whose argparser will be configured

## Returns:
    None: This method modifies the instance's argument parser in-place

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.argparser (modifies the argument parser instance)

## Constraints:
    Preconditions: 
    - self.argparser must be initialized and accessible
    - The method should be called during utility initialization/setup phase
    
    Postconditions:
    - The argument parser will contain all defined command-line options
    - Default values are set for various configuration parameters including CSV formatting options

## Side Effects:
    None: This method only configures the argument parser and doesn't perform I/O operations or external service calls

## Known Callers:
    This method is called internally by the CSVKitUtility base class during the utility setup lifecycle, specifically during the argument parsing initialization phase before the main execution logic begins.

## Why Separate Method:
    This logic is separated into its own method to follow the principle of separation of concerns, allowing the argument parsing configuration to be cleanly decoupled from the main execution logic. It also enables easier testing and maintenance of command-line interface definitions.

### `csvkit.utilities.sql2csv.SQL2CSV.main` · *method*

## Summary:
Executes a SQL query against a database and writes the results to CSV format.

## Description:
This method serves as the core execution point for converting database query results into CSV format. It handles database connection setup, SQL query execution (either from command-line argument or file input), and result formatting. The method orchestrates the entire process of connecting to a database, executing a query, and outputting the results as CSV data.

The method is part of the SQL2CSV utility class that inherits from CSVKitUtility, and follows the standard pattern of CLI utilities in csvkit where the main business logic is implemented in the main() method.

## Args:
    None - This is an instance method that operates on self

## Returns:
    None - This method performs I/O operations and does not return a value

## Raises:
    ImportError: When the required database backend is not installed for the specified connection string
    SystemExit: When input validation fails (missing query when expected)

## State Changes:
    Attributes READ: 
    - self.args.connection_string
    - self.args.query
    - self.args.input_path
    - self.args.no_header_row
    - self.writer_kwargs
    - self.output_file
    - self.argparser (via additional_input_expected call)
    
    Attributes WRITTEN:
    - self.input_file (when reading from file)

## Constraints:
    Preconditions:
    - Database connection string must be valid and backend must be installed
    - If additional input is expected (stdin is a TTY and no input file specified), a query must be provided via command-line argument or file
    - Query must be valid SQL syntax for the target database
    
    Postconditions:
    - Database connection and engine are properly closed
    - Output file contains properly formatted CSV data
    - Input file is closed when opened from disk

## Side Effects:
    - Opens and closes database connections using SQLAlchemy
    - Reads from input file or stdin when no query is provided
    - Writes CSV data to output file or stdout
    - May raise ImportError if database backend is missing
    - May raise SystemExit if validation fails

## `csvkit.utilities.sql2csv.launch_new_instance` · *function*

*No documentation generated.*

