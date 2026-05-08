# `csvpy.py`

## `csvkit.utilities.csvpy.CSVPy` · *class*

## Summary:
CSVPy is a command-line utility that loads a CSV file into an interactive Python shell with different reader modes for exploration and analysis.

## Description:
CSVPy is designed to facilitate interactive exploration of CSV data by loading it into a Python environment where users can inspect and manipulate the data. It inherits from CSVKitUtility and provides three different loading modes: standard CSV reader, DictReader for dictionary-style access, or agate Table for advanced data analysis capabilities. The utility drops users into an interactive Python shell (preferably IPython) where they can work with the loaded data.

## State:
- `input_file`: File handle pointing to the CSV input, inherited from CSVKitUtility
- `args`: Parsed command-line arguments, inherited from CSVKitUtility  
- `reader_kwargs`: Dictionary of CSV reader configuration parameters, inherited from CSVKitUtility
- `output_file`: Output file handle, inherited from CSVKitUtility
- `argparser`: Argument parser instance, inherited from CSVKitUtility

## Lifecycle:
- Creation: Instantiated by the CSVKit framework when invoked as a command-line utility with a CSV file path
- Usage: The `main()` method is called by the parent class's `run()` method, which handles input file opening and argument parsing
- Destruction: Managed automatically by Python's garbage collection; input file is properly closed by the parent class's `run()` method

## Method Map:
```mermaid
graph TD
    A[CSVPy.run()] --> B[CSVPy.main()]
    B --> C{Input validation}
    C -->|stdin| D[Error: STDIN not supported]
    C -->|file| E[Select loader type]
    E --> F{as_dict flag}
    F -->|True| G[agate.csv.DictReader]
    F -->|False| H{as_agate flag}
    H -->|True| I[agate.Table.from_csv]
    H -->|False| J[agate.csv.reader]
    J --> K[Create variable]
    G --> K
    I --> K
    K --> L[Welcome message]
    L --> M{IPython available}
    M -->|Yes| N[InteractiveShellEmbed]
    M -->|No| O[code.interact]
    N --> P[Shell session]
    O --> P
```

## Raises:
- `SystemExit`: Raised by `self.argparser.error()` when input is provided via STDIN (not supported)
- `ImportError`: Raised when IPython is not available and falls back to `code.interact()`
- Any exceptions that may occur during file operations, CSV parsing, or shell initialization

## Example:
```bash
# Load CSV file with standard reader
csvpy data.csv

# Load CSV file with DictReader
csvpy --dict data.csv

# Load CSV file with agate Table
csvpy --agate data.csv
```

After execution, users will be dropped into an interactive Python shell where they can access the loaded data:
```
Welcome! "data.csv" has been loaded in an agate.csv.reader object named "reader".
Python 3.x.x (default, ...) on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> reader
<agate.csv.reader object at 0x...>
>>> next(reader)
['column1', 'column2', 'column3']
>>> 
```

### `csvkit.utilities.csvpy.CSVPy.add_arguments` · *method*

## Summary:
Configures command-line arguments for CSV file loading options, enabling users to specify whether to load CSV data as a DictReader or as an agate table.

## Description:
This method extends the argument parser with two specialized flags that control how CSV data is processed and loaded into memory. It is part of the CSVPy utility class which provides interactive Python shell capabilities for CSV data manipulation. The method is called during the initialization phase of the CSVKitUtility framework to set up custom command-line options beyond the standard CSV processing arguments.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self.argparser
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - Must be called after self.argparser is initialized (typically during CSVPy.__init__)
    - The parent class CSVKitUtility must have been properly initialized with _init_common_parser
    
    Postconditions:
    - Two new command-line arguments are registered with self.argparser:
      * --dict flag that sets self.args.as_dict to True
      * --agate flag that sets self.args.as_agate to True

## Side Effects:
    None

### `csvkit.utilities.csvpy.CSVPy.main` · *method*

## Summary:
Loads a CSV file into a specified reader type and launches an interactive Python shell for exploration.

## Description:
This method serves as the entry point for the csvpy utility, which loads a CSV file into either a DictReader, agate.Table, or regular csv.reader object, then drops the user into an interactive Python shell (REPL) where they can explore and manipulate the loaded data. The method provides different loading modes based on command-line arguments (--dict, --agate) and ensures proper error handling for invalid input scenarios.

The csvpy utility is designed for interactive data exploration and analysis. It allows users to quickly load CSV data into Python objects and experiment with data manipulation, filtering, and analysis without writing code upfront. This is particularly useful for data scientists, analysts, and developers who want to quickly inspect and test operations on CSV datasets.

## Args:
    self: The CSVPy instance containing configuration and input file information. Must have the following attributes:
        - self.input_file: File handle for the CSV input (cannot be sys.stdin)
        - self.args: Parsed command-line arguments with as_dict and as_agate flags
        - self.reader_kwargs: Dictionary of CSV reader configuration parameters
        - self.argparser: Argument parser instance for error reporting

## Returns:
    None: This method does not return a value but initiates an interactive shell session that blocks execution until the shell exits

## Raises:
    SystemExit: Raised when input is provided via STDIN (not supported) with error message 'csvpy cannot accept input as piped data via STDIN.'
    ImportError: When IPython is not available and falls back to the standard code module for interactive session

## State Changes:
    Attributes READ: 
    - self.input_file: File handle for reading CSV data
    - self.args: Command-line arguments determining reader type
    - self.reader_kwargs: CSV reader configuration parameters
    - self.argparser: Argument parser for error reporting
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.input_file must be a valid file handle (not sys.stdin)
    - self.args must contain properly parsed command-line arguments with as_dict and as_agate flags
    - self.reader_kwargs must contain valid CSV reader keyword arguments
    - Input file must be readable and contain valid CSV data
    
    Postconditions:
    - An interactive Python shell session is initiated with the loaded CSV data
    - The shell session will exit normally or raise an exception if interrupted
    - The loaded CSV data is available in the shell as either 'reader' or 'table' variable

## Side Effects:
    - Opens and reads from the input file
    - Launches an interactive Python shell (either IPython or standard Python REPL)
    - Prints welcome message to stdout
    - May import and execute code dynamically (exec statement)
    - May import IPython or standard code module at runtime

## `csvkit.utilities.csvpy.launch_new_instance` · *function*

## Summary:
Launches a new instance of the CSVPy interactive CSV processing utility.

## Description:
Creates and executes an instance of the CSVPy class, which provides an interactive Python shell environment for exploring CSV data. This function serves as the entry point for launching the CSVPy utility, handling the instantiation and execution of the interactive CSV processing environment.

The function is typically called by the command-line interface framework when the csvpy utility is invoked, and it orchestrates the setup and execution of the interactive CSV exploration session.

## Args:
    None

## Returns:
    None

## Raises:
    SystemExit: When the underlying CSVPy utility encounters invalid input (such as STDIN usage) and exits the program
    ImportError: When IPython is not available and falls back to the standard Python interpreter
    Any exceptions that may occur during file operations, CSV parsing, or shell initialization within the CSVPy class

## Constraints:
    Preconditions:
    - The script must be running in an environment where the CSVPy class is available
    - Command-line arguments must be properly configured for the CSVKit framework
    - Input file paths (if provided) must be accessible and valid
    
    Postconditions:
    - A new CSVPy instance is created and executed
    - The interactive shell session begins (either with IPython or Python's code.interact)
    - The user is dropped into an interactive Python environment with CSV data loaded

## Side Effects:
    - Opens and reads the specified CSV input file
    - Creates an interactive Python shell session (stdout/stdin interaction)
    - May attempt to import and use IPython for enhanced interactive experience
    - May fall back to standard Python's code.interact() if IPython is unavailable
    - Outputs welcome messages and prompts to stdout

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[CSVPy()]
    B --> C[utility.run()]
    C --> D{Input validation}
    D -->|STDIN| E[SystemExit]
    D -->|file| F[Select loader type]
    F --> G{as_dict flag}
    G -->|True| H[DictReader]
    G -->|False| I{as_agate flag}
    I -->|True| J[agate.Table]
    I -->|False| K[agate.csv.reader]
    K --> L[Create variable]
    H --> L
    J --> L
    L --> M[Welcome message]
    M --> N{IPython available}
    N -->|Yes| O[InteractiveShellEmbed]
    N -->|No| P[code.interact]
    O --> Q[Shell session]
    P --> Q
```

## Examples:
```bash
# Launch CSVPy with a CSV file
csvpy data.csv

# Launch CSVPy with DictReader mode
csvpy --dict data.csv

# Launch CSVPy with agate Table mode
csvpy --agate data.csv
```

In the interactive session, users can access the loaded CSV data:
```python
>>> reader
<agate.csv.reader object at 0x...>
>>> next(reader)
['column1', 'column2', 'column3']
>>> 
```

