# `log_formatter.py`

## `onlinejudge_command.log_formatter.LogFormatter` · *class*

## Summary:
A custom logging formatter that adds color-coded output and special message handling to log records.

## Description:
The LogFormatter class extends Python's standard logging.Formatter to provide enhanced console output with color-coded log levels and special message prefix handling. It is designed to improve readability of log messages in terminal environments by applying ANSI color codes based on log severity levels and specific message patterns.

This formatter is particularly useful in command-line applications where visual distinction between different log levels and message types is important for debugging and monitoring. The class integrates with the standard logging module and maintains compatibility with existing logging configurations.

## State:
- `datefmt` (Optional[str]): Format string for timestamps, inherited from parent logging.Formatter class
- `log_colors_level` (dict): Mapping of log level numbers to color codes for standard log levels
- `log_colors_semantics` (dict): Mapping of message prefixes to color codes for semantic handling

The class inherits from logging.Formatter and maintains all its standard behavior while extending the format() method to add color support.

## Lifecycle:
- Creation: Instantiate with optional datefmt parameter to customize timestamp format
- Usage: Apply to logging handlers to format log records before output
- Destruction: Managed automatically by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[LogFormatter.__init__] --> B[logging.Formatter.__init__]
    B --> C[LogFormatter.format]
    C --> D{levelno in log_colors_level?}
    D -- Yes --> E[heading determination]
    D -- No --> F[super().format(record)]
    E --> G{message starts with prefix?}
    G -- Yes --> H[Apply semantic color]
    G -- No --> I[Apply level color]
    H --> J[Process exception info]
    I --> J
    J --> K[Return formatted message]
    F --> K
```

## Raises:
- None explicitly raised by __init__
- The format method may raise exceptions from parent class methods or from colorama operations if terminal color support fails

## Example:
```python
import logging
from onlinejudge_command.log_formatter import LogFormatter

# Create logger with custom formatter
logger = logging.getLogger('my_app')
handler = logging.StreamHandler()
formatter = LogFormatter(datefmt='%H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Use logger
logger.info("Application started")
logger.error("An error occurred")
logger.warning("This is a warning")
```

### `onlinejudge_command.log_formatter.LogFormatter.__init__` · *method*

## Summary:
Initializes a LogFormatter instance with a custom log message format that includes level name and message.

## Description:
This method sets up the logging formatter with a specific format string that displays log level names in brackets followed by the log message. It inherits from the parent logging.Formatter class and configures the formatting pattern while preserving the ability to customize the date format. This initialization ensures that all log messages follow a consistent format with level indicators.

## Args:
    datefmt (Optional[str]): Date format string for timestamp formatting. Defaults to None.

## Returns:
    None: This method does not return any value.

## Raises:
    None: This method does not explicitly raise any exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: The LogFormatter instance is properly initialized with the specified format and datefmt.

## Side Effects:
    None: This method does not perform any I/O operations or mutate external state.

### `onlinejudge_command.log_formatter.LogFormatter.format` · *method*

## Summary:
Formats log records with colored headings and special handling for exception information.

## Description:
This method customizes the formatting of log records for the LogFormatter class, applying color codes to log messages based on their severity levels and special prefixes. It handles exception information by appending stack traces and processes message prefixes to apply appropriate color coding. The method is part of a custom logging formatter that enhances console output with color-coded log levels and special message patterns.

## Args:
    record (logging.LogRecord): The log record to format

## Returns:
    str: The formatted log message string with optional color codes and exception information

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: log_colors_level, log_colors_semantics
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - record must be a valid logging.LogRecord instance
    - log_colors_level and log_colors_semantics must be defined in the module scope
    - The method assumes these global variables contain appropriate mappings
    
    Postconditions:
    - Returns a properly formatted string that may include ANSI color codes
    - Exception information is properly formatted and appended when present

## Side Effects:
    - May perform I/O operations through logging infrastructure
    - Uses colorama for terminal color support
    - Calls self.formatException() which may involve I/O operations

