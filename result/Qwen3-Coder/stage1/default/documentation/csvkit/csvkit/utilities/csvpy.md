# `csvpy.py`

## `csvkit.utilities.csvpy.CSVPy` · *class*

## Summary:
CSVPy is a command-line utility that loads CSV files into Python objects and launches an interactive Python shell for exploration and analysis.

## Description:
CSVPy enables users to load CSV data into different Python reader objects (regular reader, DictReader, or agate Table) and immediately enter an interactive Python session for data exploration. It serves as a convenient tool for quickly examining CSV datasets without writing additional code. The utility is particularly useful for data analysis, prototyping, and interactive data manipulation tasks where users want to inspect and manipulate CSV data in real-time.

The class is part of the csvkit command-line toolkit and is executed when users run the 'csvpy' command. It inherits from CSVKitUtility, which provides common CSV processing capabilities including argument parsing, file handling, and CSV reader/writer configuration.

## State:
- input_file (file-like object): Input file handle set by parent class, contains the CSV data to be loaded
- args (argparse.Namespace): Parsed command-line arguments containing as_dict and as_agate flags
- reader_kwargs (dict): Keyword arguments for CSV reader construction inherited from parent class
- description (str): Class-level description string explaining the utility's purpose

## Lifecycle:
- Creation: Instantiated by the csvkit command-line framework when executing the 'csvpy' command
- Usage: Executed via the run() method inherited from CSVKitUtility, which internally calls main()
- The main() method processes the CSV file according to specified flags and launches an interactive shell
- Destruction: Automatic cleanup handled by parent class through file handle management

## Method Map:
```mermaid
graph TD
    A[CSVKitUtility.run] --> B[CSVPy.main]
    B --> C[Input validation (stdin check)]
    C --> D[Class selection (--dict, --agate, or default)]
    D --> E[Object instantiation]
    E --> F[Interactive shell launch (IPython or code.interact)]
```

## Raises:
- SystemExit: Raised by argparser.error() when input is provided via STDIN (piped data), which is not supported by this utility
- ImportError: Raised when IPython is not available and falls back to standard Python interactive shell

## Example:
```bash
# Load CSV as regular reader
csvpy data.csv

# Load CSV as DictReader  
csvpy data.csv --dict

# Load CSV as agate Table
csvpy data.csv --agate

# With additional CSV reader options
csvpy data.csv --dict --delimiter ';' --quotechar '"'
```

In the interactive shell, users can access the loaded data through the variable named 'reader' (for regular reader/DictReader) or 'table' (for agate Table), allowing for immediate data exploration and manipulation.

### `csvkit.utilities.csvpy.CSVPy.add_arguments` · *method*

## Summary:
Adds command-line arguments to configure CSV loading behavior for interactive Python shell access.

## Description:
Configures the argument parser with options to specify how CSV data should be loaded into memory when entering the interactive Python shell. This method is called during the initialization phase of the CSVPy utility to extend the standard CSVKit argument parsing with utility-specific options.

The method adds two mutually exclusive flags that determine the data structure type for CSV loading:
- --dict: Load CSV as a DictReader object for dictionary-style access
- --agate: Load CSV as an agate Table object for advanced data analysis

This separation allows users to choose the most appropriate data structure for their interactive analysis session.

## Args:
    None: This method operates on the instance's argparser attribute and doesn't accept parameters.

## Returns:
    None: This method modifies the instance's argparser in-place and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: 
        - self.argparser: The argument parser instance used for command-line argument parsing
    
    Attributes WRITTEN:
        - self.argparser: Modified with two new command-line arguments

## Constraints:
    Preconditions:
        - The instance must have an initialized argparser attribute (typically set by CSVKitUtility.__init__)
        - The method should only be called during the initialization phase before argument parsing occurs
        
    Postconditions:
        - Two new command-line arguments are registered with the instance's argparser
        - The arguments are available for parsing when the utility executes

## Side Effects:
    None: This method only modifies the argument parser's configuration and does not perform I/O operations or external service calls.

### `csvkit.utilities.csvpy.CSVPy.main` · *method*

## Summary:
Launches an interactive Python shell with CSV data loaded into memory for exploration and analysis.

## Description:
This method provides an interactive Python environment where users can explore CSV data using Python's REPL. It supports three different CSV reading modes based on command-line arguments: DictReader for dictionary-style access, agate.Table for structured data analysis, and standard reader for basic row iteration. The method loads the CSV file into memory using the appropriate reader class and starts an interactive shell with the data available as a variable.

The method first validates that input is not from stdin (piped data), then determines the appropriate CSV reader class based on command-line flags, loads the data, and launches an interactive Python shell with the data available in the namespace.

## Args:
    self: The CSVPy instance containing configuration and input file information

## Returns:
    None: This method does not return a value but enters an interactive session

## Raises:
    SystemExit: When input is provided via stdin (piped data), which is not supported by this utility

## State Changes:
    Attributes READ: 
    - self.input_file: The input file handle being processed
    - self.args: Command-line arguments controlling reading mode (as_dict, as_agate)
    - self.reader_kwargs: Additional keyword arguments for CSV reader initialization
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - Input file must not be sys.stdin (piped data is not supported)
    - Command-line arguments must be properly parsed
    - CSV file must be readable and valid
    
    Postconditions:
    - An interactive Python shell session is initiated
    - CSV data is loaded into memory in the selected format
    - Welcome message is displayed with loading information

## Side Effects:
    - Opens an interactive Python shell (REPL) session
    - Prints welcome message to stdout
    - Dynamically imports either IPython or Python's code module
    - Reads from the input file stream
    - Executes code in the interactive shell context

## `csvkit.utilities.csvpy.launch_new_instance` · *function*

## Summary:
Creates and executes a new instance of the CSVPy command-line utility for interactive CSV data exploration.

## Description:
This function serves as the entry point for launching the csvpy command-line utility. It instantiates the CSVPy class and invokes its run method to load CSV data into Python objects and launch an interactive shell for data exploration. The function abstracts away the instantiation and execution details, providing a clean interface for the csvkit framework to initialize and run the CSV exploration utility.

This function follows the standard csvkit pattern where each command-line utility has a launch_new_instance function that creates and runs the appropriate utility class instance. It is typically called by the csvkit command-line entry points to initiate interactive CSV data exploration.

## Args:
    None

## Returns:
    None

## Raises:
    SystemExit: Raised by CSVPy.run() when input is provided via STDIN (piped data), which is not supported by this utility
    ImportError: Raised when IPython is not available and falls back to standard Python interactive shell

## Constraints:
    Preconditions:
    - The csvkit command-line environment must be properly initialized
    - Command-line arguments must be available for parsing by CSVPy
    - Standard input/output streams must be accessible
    
    Postconditions:
    - The CSVPy utility will have loaded CSV data according to its configuration
    - An interactive Python shell will be launched for data exploration
    - The process will exit when the user exits the interactive shell

## Side Effects:
    - Reads from standard input or specified input file(s)
    - Launches an interactive Python shell (either IPython or code.interact)
    - May write diagnostic messages to standard error
    - Processes command-line arguments through the csvkit argument parser

## Control Flow:
```mermaid
flowchart TD
    A[launch_new_instance called] --> B[Create CSVPy instance]
    B --> C[Call utility.run()]
    C --> D[CSVPy.run() inherits from CSVKitUtility.run()]
    D --> E[CSVPy.main() executes]
    E --> F{Input validation (stdin check)}
    F -->|STDIN| G[SystemExit raised]
    F -->|File| H[Class selection (--dict, --agate, or default)]
    H --> I[Object instantiation]
    I --> J[Interactive shell launch (IPython or code.interact)]
    J --> K[User interacts with data]
    K --> L[Shell exits]
    L --> M[Function returns]
```

## Examples:
```bash
# Load CSV as regular reader and launch interactive shell
csvpy data.csv

# Load CSV as DictReader and launch interactive shell  
csvpy data.csv --dict

# Load CSV as agate Table and launch interactive shell
csvpy data.csv --agate

# With additional CSV reader options
csvpy data.csv --dict --delimiter ';' --quotechar '"'
```

