# `cli.py`

## `src.exodus_bundler.cli.parse_args` · *function*

## Summary:
Parses command-line arguments for the Exodus ELF bundling tool and returns them as a dictionary.

## Description:
This function configures and executes an argument parser to handle command-line options for bundling ELF binary executables with their runtime dependencies. It processes positional executable arguments and various optional flags that control the bundling behavior, such as chroot environments, additional file inclusion, dependency detection, and output formatting.

The function is designed to be called by the main application entry point to convert command-line input into a structured configuration that can be passed to the bundling logic.

## Args:
    args (list[str], optional): Command-line arguments to parse. If None, sys.argv[1:] is used.
    namespace (argparse.Namespace, optional): An object to store parsed arguments. If None, a new namespace is created.

## Returns:
    dict[str, Any]: A dictionary mapping argument names to their parsed values. Keys include:
        - 'executables': List of ELF executable paths (positional argument)
        - 'chroot': Path to chroot directory (optional)
        - 'add': List of additional files to include (optional)
        - 'detect': Boolean flag for auto-detecting dependencies (optional)
        - 'no_symlink': List of files that should not be symlinked (optional)
        - 'output': Output file path (optional)
        - 'quiet': Boolean flag to suppress warnings (optional)
        - 'rename': List of new names for executables (optional)
        - 'shell_launchers': Boolean flag to force shell launchers (optional)
        - 'tarball': Boolean flag to create tarball instead of installer (optional)
        - 'verbose': Boolean flag for verbose output (optional)

## Raises:
    SystemExit: When invalid arguments are provided or help is requested.

## Constraints:
    Preconditions:
        - The function must be called with valid argument types
        - Positional 'executables' argument must be provided (nargs='+')
    Postconditions:
        - Returns a dictionary with all parsed arguments
        - All arguments are properly validated by argparse

## Side Effects:
    - Prints help text to stdout when --help is used
    - Prints error messages to stderr when invalid arguments are provided
    - May exit the program with SystemExit when parsing fails

## Control Flow:
```mermaid
flowchart TD
    A[Start parse_args] --> B{args provided?}
    B -->|Yes| C[Use provided args]
    B -->|No| D[Use sys.argv[1:]]
    C --> E[Parsing begins]
    D --> E
    E --> F[Parse executables (required)]
    F --> G[Parse chroot option]
    G --> H[Parse add option]
    H --> I[Parse detect flag]
    I --> J[Parse no_symlink option]
    J --> K[Parse output option]
    K --> L[Parse quiet flag]
    L --> M[Parse rename option]
    M --> N[Parse shell_launchers flag]
    N --> O[Parse tarball flag]
    O --> P[Parse verbose flag]
    P --> Q[Return vars(parser.parse_args())]
```

## Examples:
    # Basic usage with default arguments
    parsed_args = parse_args(['myapp'])
    
    # Usage with multiple options
    parsed_args = parse_args([
        'myapp', 
        '-c', '/path/to/chroot',
        '-a', '/lib/custom.so',
        '-o', 'bundle.tgz',
        '--tarball'
    ])
    
    # Usage with renaming
    parsed_args = parse_args([
        'oldname', 
        '-r', 'newname'
    ])

## `src.exodus_bundler.cli.configure_logging` · *function*

## Summary:
Configures the application's logging system with appropriate levels and handlers based on command-line flags.

## Description:
Sets up logging for the Exodus bundler CLI application with different behaviors based on verbosity and quiet flags. This function establishes the root logger configuration with separate handlers for stdout and stderr, allowing fine-grained control over where log messages appear based on their severity level.

## Args:
    quiet (bool): When True, sets logging level to ERROR to suppress warnings and info messages.
    verbose (bool): When True, sets logging level to INFO to enable verbose output.
    suppress_stdout (bool): When True, disables stdout logging output. Defaults to False.

## Returns:
    None: This function does not return any value.

## Raises:
    None: This function does not explicitly raise exceptions.

## Constraints:
    Preconditions:
    - The `root_logger` must be properly initialized before calling this function
    - The `quiet` and `verbose` parameters should not both be True simultaneously (though the function handles this gracefully)
    
    Postconditions:
    - The global root_logger is configured with appropriate log level
    - Either stdout or stderr handlers are added to the root_logger based on suppress_stdout flag

## Side Effects:
    - Modifies the global root_logger configuration
    - Adds StreamHandlers to the root_logger for stdout and/or stderr
    - Sets formatters and filters on the added handlers

## Control Flow:
```mermaid
flowchart TD
    A[configure_logging called] --> B{quiet AND NOT verbose?}
    B -- Yes --> C[Set log_level to ERROR]
    B -- No --> D{verbose AND NOT quiet?}
    D -- Yes --> E[Set log_level to INFO]
    D -- No --> F[Set log_level to WARN (default)]
    F --> G[Set root_logger level]
    G --> H[Create stderr_handler]
    H --> I[Add stderr_filter to stderr_handler]
    I --> J[Add stderr_handler to root_logger]
    J --> K{suppress_stdout?}
    K -- Yes --> L[Return]
    K -- No --> M[Create stdout_handler]
    M --> N[Add stdout_filter to stdout_handler]
    N --> O[Add stdout_handler to root_logger]
```

## Examples:
    # Configure logging for quiet mode
    configure_logging(quiet=True, verbose=False)
    
    # Configure logging for verbose mode  
    configure_logging(quiet=False, verbose=True)
    
    # Configure logging with stdout suppressed
    configure_logging(quiet=False, verbose=False, suppress_stdout=True)
```

## `src.exodus_bundler.cli.StderrFilter` · *class*

## Summary:
A logging filter that permits only WARNING and ERROR level messages to pass through.

## Description:
The StderrFilter class is designed to filter log records, allowing only WARNING and ERROR level messages to be processed further. This is useful for directing important messages to stderr while suppressing less critical INFO and DEBUG messages. The class extends Python's standard logging.Filter base class and implements the required filter() method to control message flow based on log level.

## State:
- The class maintains no instance state beyond what is inherited from logging.Filter
- The filter method receives a logging.LogRecord object as input
- No constructor parameters are required as it's a simple filter with fixed behavior

## Lifecycle:
- Creation: Instantiated without arguments as part of standard logging configuration
- Usage: Automatically invoked by the logging system when processing log records
- Destruction: Managed automatically by Python's garbage collection when no longer referenced

## Method Map:
```mermaid
graph TD
    A[Log Record] --> B[StderrFilter.filter()]
    B --> C{Level No in (WARN,ERROR)?}
    C -->|Yes| D[Allow Message]
    C -->|No| E[Suppress Message]
```

## Raises:
- No exceptions are raised by the filter method under normal operation
- The filter method may raise AttributeError if the record parameter doesn't have a levelno attribute (though this would be unusual in standard logging usage)

## Example:
```python
import logging
from exodus_bundler.cli import StderrFilter

# Configure logger with the filter
logger = logging.getLogger('example')
handler = logging.StreamHandler(sys.stderr)
handler.addFilter(StderrFilter())
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Only WARNING and ERROR messages will be output to stderr
logger.info("This will be suppressed")  # Won't appear
logger.warning("This will appear")      # Will appear
logger.error("This will also appear")   # Will appear
```

### `src.exodus_bundler.cli.StderrFilter.filter` · *method*

## Summary:
Filters log records to permit only WARNING and ERROR level messages to be written to standard error.

## Description:
This method implements a logging filter that determines whether a log record should be processed by the stderr handler. It is designed to route only warning and error level messages to standard error output while allowing other log levels to be handled by different handlers (such as stdout).

The filter is used in the CLI module's logging configuration to separate warning and error messages from debug and info messages, ensuring appropriate output destinations based on message severity.

## Args:
    record (logging.LogRecord): A log record object containing the logging event information

## Returns:
    bool: True if the record's level number is either logging.WARN (30) or logging.ERROR (40), False otherwise

## Raises:
    None: This method does not raise any exceptions

## State Changes:
    Attributes READ: None - this method only reads properties from the record parameter
    Attributes WRITTEN: None - this method does not modify any instance attributes

## Constraints:
    Preconditions: 
    - The record parameter must be a valid logging.LogRecord instance
    - The record.levelno attribute must be accessible and represent a valid logging level
    
    Postconditions:
    - The method returns a boolean value indicating whether the record should be filtered
    - The returned value determines whether the log record will be processed by the stderr handler

## Side Effects:
    None: This method performs no I/O operations or external service calls

## `src.exodus_bundler.cli.StdoutFilter` · *class*

## Summary:
A logging filter that permits only DEBUG and INFO level log records to pass through.

## Description:
The StdoutFilter class is designed to filter log records, allowing only those with DEBUG or INFO severity levels to be processed further. This is commonly used to control logging output sent to standard output, ensuring that verbose DEBUG messages and informational messages are displayed while suppressing WARNING, ERROR, and CRITICAL level messages.

This filter is particularly useful in command-line interfaces where users want to see informative output without being overwhelmed by debug details or error messages.

## State:
- The class has no instance attributes beyond what's inherited from logging.Filter
- The filter method receives a log record object and returns a boolean value
- No class invariants apply as this is a simple filtering mechanism

## Lifecycle:
- Creation: Instantiated automatically by the logging system when configured as a filter
- Usage: Called internally by Python's logging framework for each log record
- Destruction: Managed by Python's garbage collection when no longer referenced

## Method Map:
```mermaid
graph TD
    A[Log Record] --> B[StdoutFilter.filter()]
    B --> C{Level in (DEBUG,INFO)?}
    C -->|Yes| D[Return True]
    C -->|No| E[Return False]
```

## Raises:
- No exceptions are raised by the filter method itself
- The constructor (__init__) does not raise exceptions as it inherits from logging.Filter with no custom initialization

## Example:
```python
import logging
from exodus_bundler.cli import StdoutFilter

# Configure logger with the filter
logger = logging.getLogger('my_logger')
handler = logging.StreamHandler(sys.stdout)
handler.addFilter(StdoutFilter())
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# These will be displayed:
logger.info("This is an info message")
logger.debug("This is a debug message")

# These will be filtered out:
logger.warning("This is a warning")
logger.error("This is an error")
```

### `src.exodus_bundler.cli.StdoutFilter.filter` · *method*

## Summary:
Filters log records to allow only DEBUG and INFO level messages to pass through to standard output.

## Description:
This method implements a logging filter that selectively processes log records based on their severity level. It is designed to be used with Python's logging module to control which messages are displayed on standard output. The filter accepts only records with DEBUG or INFO level severity, blocking all other levels including WARNING, ERROR, and CRITICAL.

## Args:
    record (logging.LogRecord): A logging record object containing information about the log event including levelno, message, and other metadata.

## Returns:
    bool: True if the record's level number is either logging.DEBUG (10) or logging.INFO (20), False otherwise.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: None - this method only reads from the record parameter
    Attributes WRITTEN: None - this method does not modify any instance attributes

## Constraints:
    Preconditions: The record parameter must be a valid logging.LogRecord object with a levelno attribute
    Postconditions: The method always returns a boolean value indicating whether the record should be processed

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only evaluates the level number of the log record.

## `src.exodus_bundler.cli.main` · *function*

## Summary:
Entry point for the Exodus ELF bundling command-line interface that processes arguments, configures logging, and orchestrates bundle creation.

## Description:
The main function serves as the central coordination point for the Exodus bundling tool, handling command-line argument parsing, output path resolution, logging setup, and delegation to the core bundling logic. It manages the complete workflow from user input to bundle generation, including special handling for stdin input and error recovery.

This function extracts the core bundling responsibility from the CLI layer to maintain clean separation of concerns, ensuring that argument parsing, logging configuration, and error handling remain distinct from the actual bundle creation logic.

## Args:
    args (list[str], optional): Command-line arguments to parse. If None, sys.argv[1:] is used.
    namespace (argparse.Namespace, optional): An object to store parsed arguments. If None, a new namespace is created.

## Returns:
    None: This function does not return a value directly, but may cause program termination via sys.exit().

## Raises:
    SystemExit: Raised when invalid arguments are provided or help is requested during argument parsing.
    FatalError: Raised when bundle creation fails, causing program termination with exit code 1.

## Constraints:
    Preconditions:
        - At least one executable must be specified in the executables list.
        - The number of rename entries must not exceed the number of executables.
        - All specified file paths must exist and be valid files (not directories).
        - The output parameter must be a valid template string.
    Postconditions:
        - The output file is created with appropriate content and permissions.
        - Temporary resources are cleaned up upon successful completion or exception.

## Side Effects:
    - Reads command-line arguments from sys.argv or provided args parameter
    - Configures global logging settings via configure_logging
    - May read from stdin when not running in a terminal (when sys.stdin.isatty() returns False)
    - Creates output file at specified location
    - Writes to stdout/stderr for logging and bundle content
    - May terminate the process with sys.exit()

## Control Flow:
```mermaid
flowchart TD
    A[main called] --> B[Parse arguments with parse_args]
    B --> C{output is None?}
    C -- Yes --> D{stdout isatty?}
    D -- Yes --> E[Set default output path: ./exodus-{{executables}}-bundle.{{extension}}]
    D -- No --> F[Set output to '-']
    C -- No --> G[Continue with provided output]
    G --> H[Extract quiet/verbose flags from args]
    H --> I[Calculate suppress_stdout = args['output'] == '-']
    I --> J[Configure logging with quiet, verbose, suppress_stdout]
    J --> K{sys.stdin.isatty() returns False?}
    K -- Yes --> L[Read stdin content]
    L --> M[Extract paths from stdin using extract_paths]
    M --> N[Append extracted paths to args['add']]
    N --> O[Try create_bundle(**args)]
    O --> P{FatalError raised?}
    P -- Yes --> Q[Log "Fatal error encountered, exiting." to stderr]
    Q --> R[Log fatal error details if verbose]
    R --> S[Exit with code 1]
    P -- No --> T[Return normally]
```

## Examples:
    # Basic usage
    main(['myapp'])
    
    # With output specification
    main(['myapp', '-o', 'bundle.sh'])
    
    # With verbose output
    main(['myapp', '--verbose'])
    
    # Using stdin for additional paths (non-interactive mode)
    echo "/lib/libfoo.so" | main(['myapp'])
    
    # Interactive mode with default output (when stdout is a terminal)
    main(['myapp'])  # Will use default output path when run in terminal
```

