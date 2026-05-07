# `log_formatter.py`

## `onlinejudge_command.log_formatter.LogFormatter` · *class*

## Summary:
A custom logging formatter that enhances log output with color coding and semantic message handling.

## Description:
The LogFormatter class extends Python's standard logging.Formatter to provide enhanced formatting capabilities for log messages. It applies color coding based on log levels and processes special message prefixes with semantic coloring to improve log readability.

This formatter uses a predefined format string '[%(levelname)s] %(message)s' and custom logic to apply colors to log messages based on their severity levels and special prefixes.

## State:
- Inherits from logging.Formatter with standard formatter functionality
- Uses a fixed format string '[%(levelname)s] %(message)s'
- Relies on external global variables `log_colors_level` and `log_colors_semantics` for color mapping
- These external variables must be defined in the module scope for proper operation

## Lifecycle:
- Creation: Instantiate with optional datefmt parameter (same as logging.Formatter)
- Usage: Set as formatter for logging handlers to process log records
- Destruction: Standard Python object cleanup

## Method Map:
```mermaid
graph TD
    A[LogFormatter.format] --> B{record.levelno in log_colors_level?}
    B -- No --> C[super().format(record)]
    B -- Yes --> D[Initialize heading = None]
    D --> E[Get message with record.getMessage()]
    E --> F{message empty AND exc_info None?}
    F -- Yes --> G[heading = '']
    F -- No --> H[Check semantic prefixes]
    H --> I{Semantic prefix found?}
    I -- Yes --> J[Set heading and strip prefix]
    I -- No --> K[Use level-based color]
    J --> L[Process exception info if present]
    K --> L
    L --> M{heading empty?}
    M -- Yes --> N[Return message]
    M -- No --> O[Return heading + message]
    C --> P[Return formatted result]
    P --> Q[End]
```

## Raises:
- AttributeError: If `log_colors_level` or `log_colors_semantics` are not defined in module scope
- No explicit exceptions from __init__ method itself

## Example:
```python
import logging
from onlinejudge_command.log_formatter import LogFormatter

# Setup logger with custom formatter
logger = logging.getLogger('example')
handler = logging.StreamHandler()
formatter = LogFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Use logger
logger.info("This is an info message")
logger.error("This is an error message")
```

### `onlinejudge_command.log_formatter.LogFormatter.__init__` · *method*

## Summary:
Initializes a LogFormatter instance with a standardized log message format.

## Description:
Configures the logger to display log messages with severity level prefixes in a consistent format. This method sets up the formatting pattern to include the log level in brackets followed by the actual message, making log output more readable and structured.

## Args:
    datefmt (Optional[str]): Date format string for timestamp formatting. Defaults to None.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: Initializes internal formatting state inherited from parent logging.Formatter class

## Constraints:
    Preconditions: None
    Postconditions: The LogFormatter instance is properly configured with the specified format and date format.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `onlinejudge_command.log_formatter.LogFormatter.format` · *method*

## Summary:
Formats log records with color-coded headings, special prefix handling, and exception formatting for enhanced readability.

## Description:
This method customizes log record formatting by applying color codes to log levels and handling special message prefixes that start with predefined keywords. When a log record's level is configured for coloring, it applies appropriate color codes to the message header while preserving the original message content.

The method is invoked during the logging process when a log record needs to be converted to a string format for output. It's part of the LogFormatter class that extends Python's standard logging.Formatter.

## Args:
    record (logging.LogRecord): The log record to format, containing level information, message, and exception data.

## Returns:
    str: The formatted log message string. For log levels not configured for coloring, returns parent class formatted output. For colored levels, returns a colorized message with optional heading prefix and formatted exception information.

## Raises:
    None explicitly raised - relies on parent class behavior for error handling.

## State Changes:
    Attributes READ: 
    - log_colors_level (external dependency dictionary mapping log levels to colors)
    - log_colors_semantics (external dependency dictionary mapping message prefixes to colors)

## Constraints:
    Preconditions:
    - The record parameter must be a valid logging.LogRecord instance
    - log_colors_level and log_colors_semantics must be properly initialized dictionaries
    - The method assumes colorama is available for color support
    
    Postconditions:
    - Returns a properly formatted string suitable for logging output
    - Exception information is correctly formatted when present in record.exc_info
    - Empty messages with no exception info result in empty heading string
    - Messages with matching prefixes get their prefix stripped and color applied

## Side Effects:
    None directly - but depends on external colorama library for terminal coloring
    Calls parent class format() method via super().format() when log level is not in log_colors_level
    Calls self.formatException() when exception info is present in record.exc_info

