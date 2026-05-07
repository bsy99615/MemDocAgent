# `cli.py`

## `csvkit.cli.LazyFile` · *class*

*No documentation generated.*

### `csvkit.cli.LazyFile.__init__` · *method*

*No documentation generated.*

### `csvkit.cli.LazyFile.__getattr__` · *method*

*No documentation generated.*

### `csvkit.cli.LazyFile.__iter__` · *method*

*No documentation generated.*

### `csvkit.cli.LazyFile.close` · *method*

## Summary:
Closes a lazily opened file handle and resets the internal state to indicate the file is no longer open.

## Description:
The close method is responsible for properly closing the underlying file handle when a LazyFile instance is no longer needed. It only performs the actual close operation if the file was previously opened lazily (i.e., when `_is_lazy_opened` is True). This method ensures proper resource cleanup and resets the internal state flags to reflect that the file is closed.

This method is typically called as part of a resource management pattern, either explicitly by user code or implicitly through context managers or iteration protocols that automatically close files when done.

## Args:
    None

## Returns:
    None

## Raises:
    AttributeError: If the underlying file handle (`self.f`) does not have a close method when attempting to close it.
    Exception: Any exception that might occur during the actual file closing operation, propagated from the underlying file's close method.

## State Changes:
    Attributes READ: 
        - self._is_lazy_opened: Checked to determine if the file needs to be closed
        - self.f: Accessed to call its close method
    
    Attributes WRITTEN:
        - self.f: Set to None after closing
        - self._is_lazy_opened: Set to False after closing

## Constraints:
    Preconditions:
        - The method should only be called on LazyFile instances that were created with a valid file initialization function
        - The file handle (`self.f`) should be properly initialized if the file was previously opened
        
    Postconditions:
        - If the file was open, it will be closed and the file handle will be set to None
        - The `_is_lazy_opened` flag will be set to False
        - The LazyFile instance can be reused for subsequent operations

## Side Effects:
    - I/O operation: Closes the underlying file handle, releasing system resources
    - State mutation: Modifies internal state variables to indicate the file is closed

### `csvkit.cli.LazyFile.__next__` · *method*

*No documentation generated.*

### `csvkit.cli.LazyFile._open` · *method*

*No documentation generated.*

## `csvkit.cli.CSVKitUtility` · *class*

*No documentation generated.*

### `csvkit.cli.CSVKitUtility.__init__` · *method*

*No documentation generated.*

### `csvkit.cli.CSVKitUtility.add_arguments` · *method*

*No documentation generated.*

### `csvkit.cli.CSVKitUtility.run` · *method*

*No documentation generated.*

### `csvkit.cli.CSVKitUtility.main` · *method*

## Summary:
Abstract method that must be implemented by subclasses to provide the core functionality of CSV processing utilities.

## Description:
This method serves as the entry point for the core logic of each CSV utility implementation. It is called by the `run()` method after the input file is properly initialized and configured. The method is designed to be overridden by concrete implementations that define specific CSV processing behaviors.

## Args:
    self: The instance of the CSVKitUtility subclass implementing this method.

## Returns:
    This method does not return a value directly. Its behavior depends entirely on the specific implementation in each subclass.

## Raises:
    NotImplementedError: Always raised by the base implementation, indicating that subclasses must provide their own implementation.

## State Changes:
    Attributes READ: 
    - self.args: Contains parsed command-line arguments
    - self.override_flags: Controls which command-line flags are available
    - self.input_file: The opened input file handle (when not overridden by flags)
    
    Attributes WRITTEN:
    - self.input_file: May be modified when opening/closing files (depending on override_flags)

## Constraints:
    Preconditions:
    - This method must be implemented by all subclasses of CSVKitUtility
    - The `run()` method must be called to properly initialize the utility before this method is invoked
    
    Postconditions:
    - The method executes the specific CSV processing logic defined by the subclass implementation
    - Input file is properly managed according to override_flags configuration

## Side Effects:
    - May perform I/O operations when reading from input files
    - May write to output streams (stdout or specified output file)
    - May close input files when not overridden by flags
    - May raise exceptions that are handled by the parent `run()` method

### `csvkit.cli.CSVKitUtility._init_common_parser` · *method*

## Summary
Initializes a common argument parser with standard CSV processing options for CSVKit utilities.

## Description
Configures an `argparse.ArgumentParser` instance with a comprehensive set of command-line arguments commonly used for CSV file processing. This method sets up parsing options for file input, delimiter handling, quoting styles, encoding, locale settings, and various CSV-specific behaviors. The parser is stored in `self.argparser` for later use by the utility.

This method is designed to be called during the initialization of CSVKit utility classes to establish a consistent command-line interface across all utilities in the toolkit.

## Args
    None

## Returns
    None

## Raises
    None explicitly raised

## State Changes
    Attributes READ: 
        - self.description: Used as the parser's description
        - self.epilog: Used as the parser's epilog  
        - self.override_flags: Used to conditionally enable/disable arguments
    
    Attributes WRITTEN:
        - self.argparser: Set to the newly created ArgumentParser instance

## Constraints
    Preconditions:
        - The calling class must have `description` and `epilog` attributes defined
        - The calling class must have `override_flags` attribute defined as a collection-like object
        - This method should only be called once during object initialization

    Postconditions:
        - `self.argparser` is initialized as an `argparse.ArgumentParser` instance
        - The parser contains all standard CSV processing arguments based on `override_flags`
        - Parser configuration is complete and ready for argument parsing

## Side Effects
    None

### `csvkit.cli.CSVKitUtility._open_input_file` · *method*

*No documentation generated.*

### `csvkit.cli.CSVKitUtility._extract_csv_reader_kwargs` · *method*

*No documentation generated.*

### `csvkit.cli.CSVKitUtility._extract_csv_writer_kwargs` · *method*

*No documentation generated.*

### `csvkit.cli.CSVKitUtility._install_exception_handler` · *method*

## Summary:
Installs a custom exception handler that provides user-friendly error messages for common CSV processing issues.

## Description:
Configures the global exception handler to provide more informative error messages to users when exceptions occur during CSV processing. The handler displays detailed error information when the verbose flag is enabled, or provides simplified, helpful messages for common encoding issues when disabled.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: self.args.encoding, self.args.verbose
    Attributes WRITTEN: sys.excepthook

## Constraints:
    Preconditions: 
    - self.args must be initialized with parsed command-line arguments
    - The method should be called during object initialization
    - sys module must be available
    
    Postconditions:
    - sys.excepthook is replaced with a custom handler function
    - Error messages are written to stderr

## Side Effects:
    - Modifies the global sys.excepthook
    - Writes error messages to stderr
    - May change the behavior of unhandled exception reporting

### `csvkit.cli.CSVKitUtility.get_column_types` · *method*

*No documentation generated.*

### `csvkit.cli.CSVKitUtility.get_column_offset` · *method*

*No documentation generated.*

### `csvkit.cli.CSVKitUtility.skip_lines` · *method*

*No documentation generated.*

### `csvkit.cli.CSVKitUtility.get_rows_and_column_names_and_column_ids` · *method*

*No documentation generated.*

### `csvkit.cli.CSVKitUtility.print_column_names` · *method*

*No documentation generated.*

### `csvkit.cli.CSVKitUtility.additional_input_expected` · *method*

*No documentation generated.*

## `csvkit.cli.isatty` · *function*

*No documentation generated.*

## `csvkit.cli.default_str_decimal` · *function*

*No documentation generated.*

## `csvkit.cli.default_float_decimal` · *function*

*No documentation generated.*

## `csvkit.cli.make_default_headers` · *function*

*No documentation generated.*

## `csvkit.cli.match_column_identifier` · *function*

*No documentation generated.*

## `csvkit.cli.parse_column_identifiers` · *function*

*No documentation generated.*

