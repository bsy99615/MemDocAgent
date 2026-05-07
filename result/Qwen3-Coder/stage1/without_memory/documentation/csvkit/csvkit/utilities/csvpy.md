# `csvpy.py`

## `csvkit.utilities.csvpy.CSVPy` · *class*

*No documentation generated.*

### `csvkit.utilities.csvpy.CSVPy.add_arguments` · *method*

*No documentation generated.*

### `csvkit.utilities.csvpy.CSVPy.main` · *method*

## Summary:
Launches an interactive Python shell with CSV data loaded into a variable for exploration and analysis.

## Description:
This method provides an interactive environment for working with CSV files by loading the data into a variable and starting either an IPython or Python interactive shell. It supports three different CSV reading modes: DictReader, agate.Table, or regular CSV reader, depending on command-line arguments. The method is designed to enable exploratory data analysis in an interactive session.

## Args:
    self: The CSVPy utility instance containing configuration and input file information

## Returns:
    None: This method does not return a value; it starts an interactive shell session

## Raises:
    SystemExit: Raised by self.argparser.error when input is piped via STDIN

## State Changes:
    Attributes READ: 
    - self.input_file: The input file handle being processed
    - self.input_file.name: Name of the input file for display purposes
    - self.args: Command-line arguments parsed by the utility
    - self.reader_kwargs: Additional keyword arguments for CSV reader configuration
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.input_file must not be sys.stdin (piped input is not supported)
    - self.args.as_dict, self.args.as_agate, or neither must be set to determine reading mode
    - self.reader_kwargs must contain valid keyword arguments for the chosen CSV reader class
    
    Postconditions:
    - An interactive shell session is started with CSV data available in the namespace
    - The appropriate CSV reader class is selected based on command-line flags

## Side Effects:
    - Starts an interactive terminal session (IPython or Python REPL)
    - Dynamically imports IPython.frontend.terminal.embed.InteractiveShellEmbed or code module
    - Executes code using exec() to bind the CSV data variable in the IPython namespace
    - Prints welcome message to terminal
    - Reads from the input file stream

## `csvkit.utilities.csvpy.launch_new_instance` · *function*

*No documentation generated.*

