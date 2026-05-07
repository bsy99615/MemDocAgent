# `log_formatter.py`

## `onlinejudge_command.log_formatter.LogFormatter` · *class*

## Summary:
A custom logging formatter that provides colorized console output with semantic prefix handling for enhanced log readability.

## Description:
The LogFormatter class extends Python's standard logging.Formatter to provide enhanced console output with color coding based on log levels and semantic message prefixes. It is designed to improve readability of log messages in terminal environments by applying appropriate colors to different types of log entries.

This formatter is intended to be used with Python's logging system and provides specialized formatting logic for console output. It handles special cases like semantic prefixes (e.g., "ERROR:", "WARNING:") by applying colors based on the semantic meaning rather than the log level itself.

## State:
- `datefmt` (Optional[str]): Passed to parent constructor for date formatting. Default is None.
- `log_colors_level` (dict): Global dictionary mapping log level integers to colorama color codes. Not an instance attribute but accessed globally.
- `log_colors_semantics` (dict): Global dictionary mapping semantic prefixes to colorama color codes. Not an instance attribute but accessed globally.

## Lifecycle:
- Creation: Instantiate with optional datefmt parameter. Requires colorama to be properly initialized for color support.
- Usage: Intended to be used with logging handlers as a formatter for LogRecord objects.
- Destruction: No special cleanup required; relies on Python's garbage collection.

## Method Map:
```mermaid
graph TD
    A[LogFormatter.__init__] --> B[super().__init__]
    B --> C[Set fmt = '[%(levelname)s] %(message)s']
    A --> D[Return]
    
    E[LogFormatter.format] --> F[Check record.levelno in log_colors_level]
    F --> G{Yes}
    G --> H[Initialize heading = None]
    H --> I[Get message via record.getMessage()]
    I --> J{message empty and no exc_info}
    J --> K{Yes}
    K --> L[heading = '']
    J --> M{No}
    M --> N[Check semantic prefixes]
    N --> O{Semantic prefix found}
    O --> P[heading = color for semantic]
    P --> Q[message = stripped message]
    O --> R{No semantic prefix}
    R --> S[heading = color for level]
    S --> T[Check record.exc_info]
    T --> U{exc_info exists}
    U --> V[message += formatted exception]
    U --> W[Return heading + message]
    G --> X{No}
    X --> Y[super().format(record)]
```

## Raises:
- Inherits standard logging exceptions from parent Formatter class (e.g., TypeError if invalid format string)
- May raise AttributeError if global variables log_colors_level or log_colors_semantics are not properly initialized

## Example:
```python
import logging
from onlinejudge_command.log_formatter import LogFormatter

# Setup logger with custom formatter
logger = logging.getLogger('my_app')
handler = logging.StreamHandler()
formatter = LogFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Usage
logger.info("Application started")
logger.error("An error occurred")
logger.warning("This is a warning")
```

### `onlinejudge_command.log_formatter.LogFormatter.__init__` · *method*

## Summary:
Initializes a log formatter with a standardized message format that includes log level and message.

## Description:
Configures the LogFormatter instance to format log messages with a consistent prefix containing the log level, making log output more readable and structured. This method sets up the base logging formatter with a predefined format string while allowing customization of the date format.

## Args:
    datefmt (Optional[str]): Date format string for timestamp formatting. Defaults to None.

## Returns:
    None: This method does not return any value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: The LogFormatter instance is properly initialized with the specified format and date format.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `onlinejudge_command.log_formatter.LogFormatter.format` · *method*

## Summary:
Formats log records with colorized output and semantic prefix handling for enhanced console readability.

## Description:
Customizes log record formatting to provide colored output for different log levels and special message patterns. When a log record's level is supported by color configuration, it applies appropriate terminal colors to the message. Special handling is provided for messages starting with semantic prefixes (like "ERROR:", "WARNING:") which get colorized according to their semantic meaning rather than log level. If the log record contains exception information, it's properly formatted and appended to the message.

## Args:
    record (logging.LogRecord): The log record to format, containing levelno, getMessage(), and exc_info attributes

## Returns:
    str: Formatted log message string. If log level is not configured for colors, returns parent formatter result. Otherwise, returns colorized message with optional semantic prefix handling and exception formatting.

## Raises:
    None explicitly raised - inherits standard logging exceptions from parent formatter

## State Changes:
    Attributes READ: 
    - record.levelno (integer log level)
    - record.getMessage() (method call returning formatted message)
    - record.exc_info (exception info tuple or None)
    - log_colors_level (global dict mapping log levels to color codes)
    - log_colors_semantics (global dict mapping semantic prefixes to color codes)

## Constraints:
    Preconditions:
    - record must be a valid logging.LogRecord instance
    - log_colors_level and log_colors_semantics must be properly initialized global dictionaries
    - Colorama must be imported and configured for terminal color support
    
    Postconditions:
    - Returns a properly formatted string for console display
    - If log level is not configured for colors, delegates to parent formatter using super().format(record)
    - If log level is configured for colors but message is empty and no exception, returns empty string
    - If log level is configured for colors and message has semantic prefix, returns colorized prefix + stripped message
    - If log level is configured for colors and no semantic prefix, returns colorized log level + message
    - If exception info is present, appends formatted exception to message

## Side Effects:
    None - This method is purely functional and doesn't cause external I/O or state changes

