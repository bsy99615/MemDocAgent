# `csvpy.py`

## `csvkit.utilities.csvpy.CSVPy` · *class*

## Summary:
CSVPy is a command-line utility that loads CSV files into Python reader objects and launches an interactive Python shell for exploration.

## Description:
CSVPy serves as an interactive CSV exploration tool that loads CSV data into different Python objects (regular reader, DictReader, or agate Table) and drops users into an interactive Python session for analysis. It's particularly useful for quickly examining CSV data structures, testing data processing logic, and exploring datasets interactively without writing code.

The utility provides three loading modes through command-line flags:
- Default mode: Loads CSV into a standard agate.csv.reader object
- --dict flag: Loads CSV into a agate.csv.DictReader object for dictionary-style access
- --agate flag: Loads CSV into an agate.Table object for advanced data analysis operations

This class is typically instantiated by the csvkit command-line framework and invoked through the standard csvkit utility runner.

## State:
- Inherits all state from CSVKitUtility including argparser, args, input_file, output_file, reader_kwargs, and writer_kwargs
- `description`: Class variable set to 'Load a CSV file into a CSV reader and then drop into a Python shell.'
- No additional instance attributes beyond those inherited from the parent class

## Lifecycle:
Creation: Instantiated automatically by the csvkit framework when the csvpy command is invoked. Requires proper command-line arguments to be passed to the constructor.

Usage: 
1. Command-line invocation with CSV file argument and optional flags (--dict, --agate)
2. The run() method from CSVKitUtility orchestrates execution:
   - Validates input file isn't stdin (raises error if so)
   - Determines appropriate reader class based on flags
   - Creates the reader object with proper arguments
   - Displays welcome message with loaded object information
   - Launches interactive Python shell (IPython if available, falls back to standard code.interact)

Destruction: Automatic cleanup handled by the parent CSVKitUtility's run() method, which properly closes input files.

## Method Map:
```mermaid
graph TD
    A[run()] --> B[main()]
    B --> C[validate_input_file()]
    B --> D[determine_reader_class()]
    B --> E[create_reader_object()]
    B --> F[display_welcome_message()]
    B --> G[launch_interactive_shell()]
    G --> H[try_IPython]
    G --> I[fallback_to_code_interact]
```

## Raises:
- SystemExit: Raised by self.argparser.error() when input is provided via stdin (not supported)
- ImportError: Raised when IPython is not available and fallback to standard code.interact fails

## Example:
```python
# Load CSV into regular reader and launch interactive shell
$ csvpy data.csv

# Load CSV into DictReader and launch interactive shell  
$ csvpy --dict data.csv

# Load CSV into agate Table and launch interactive shell
$ csvpy --agate data.csv

# After launching, you can interact with the loaded data:
# >>> reader  # Shows the reader object
# >>> next(reader)  # Get first row
# >>> list(reader)  # Convert to list
```

### `csvkit.utilities.csvpy.CSVPy.add_arguments` · *method*

*No documentation generated.*

### `csvkit.utilities.csvpy.CSVPy.main` · *method*

## Summary:
Launches an interactive Python shell with CSV data loaded for exploration and analysis.

## Description:
Provides an interactive environment where users can examine and manipulate CSV data using Python's REPL. The method loads the specified CSV file into a variable using one of three possible readers (agate.csv.reader, agate.csv.DictReader, or agate.Table.from_csv) based on command-line arguments, then starts an interactive shell session.

## Args:
    self: The instance of the CSVPy class containing configuration and input file information.

## Returns:
    None: This method does not return a value but enters an interactive shell session.

## Raises:
    SystemExit: Raised by self.argparser.error() when input is provided via STDIN.

## State Changes:
    Attributes READ: 
    - self.input_file: Used to check if input is from stdin and to get filename
    - self.args: Used to determine which CSV reader class to use
    - self.reader_kwargs: Passed to the CSV reader constructor
    - self.argparser: Used to raise error when input is from stdin

## Constraints:
    Preconditions:
    - Input file must not be sys.stdin (piped data is not supported)
    - Command-line arguments must be properly parsed
    - CSV file must exist and be readable
    
    Postconditions:
    - An interactive shell session is started with CSV data loaded in a variable
    - The shell session will continue until user exits manually

## Side Effects:
    - Opens an interactive terminal session
    - May import IPython or Python's code module
    - Prints welcome message to terminal
    - Blocks execution until shell session ends

## `csvkit.utilities.csvpy.launch_new_instance` · *function*

## Summary:
Launches a new CSV exploration session by creating and executing a CSVPy utility instance.

## Description:
Creates a CSVPy utility instance and executes its run method to initiate an interactive Python shell with loaded CSV data. This function serves as the entry point for the csvpy command-line utility, enabling users to explore CSV datasets interactively in a Python environment.

The function follows the standard csvkit pattern where command-line utilities are instantiated and executed through a dedicated launch function. This approach provides a clean separation between utility creation and execution, making the code more testable and maintainable.

## Args:
    None

## Returns:
    None

## Raises:
    SystemExit: Raised by CSVPy.run() when input is provided via stdin (not supported) or when argument validation fails
    ImportError: Raised when IPython is not available and fallback to standard code.interact fails
    Various exceptions from file I/O operations handled by the parent CSVKitUtility class

## Constraints:
    Preconditions:
    - Command-line arguments must be available via sys.argv for parsing
    - Standard input/output streams must be accessible
    - Required CSV processing dependencies must be available
    - Input files (if specified) must be readable
    
    Postconditions:
    - A CSVPy utility instance is created and executed
    - CSV data is loaded into a Python reader object (standard reader, DictReader, or agate.Table)
    - An interactive Python shell is launched for data exploration
    - All temporary resources are properly cleaned up

## Side Effects:
    - Reads from standard input or specified input files (via CSVKitUtility's input_file handling)
    - Writes to standard output or specified output files (via CSVKitUtility's output_file handling)
    - Processes command-line arguments from sys.argv through CSVKitUtility's argument parser
    - May display usage information or error messages to stderr
    - Launches an interactive Python shell (IPython if available, falls back to standard code.interact)

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance()] --> B[Create CSVPy() instance]
    B --> C[Call utility.run()]
    C --> D{Input file validation}
    D -->|stdin| E[Raise SystemExit]
    D -->|file| F[Parse command-line args]
    F --> G[Determine reader class (--dict/--agate)]
    G --> H[Create reader object]
    H --> I[Display welcome message]
    I --> J[Launch interactive shell]
    J --> K{IPython available?}
    K -->|Yes| L[Launch IPython shell]
    K -->|No| M[Launch code.interact]
```

## Examples:
```bash
# Launch interactive session with CSV data loaded as standard reader
csvpy data.csv

# Launch interactive session with CSV data loaded as DictReader
csvpy --dict data.csv

# Launch interactive session with CSV data loaded as agate.Table
csvpy --agate data.csv

# After launching, you can interact with the loaded data:
# >>> reader  # Shows the reader object
# >>> next(reader)  # Get first row
# >>> list(reader)  # Convert to list
```

