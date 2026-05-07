# `log_formatter.py`

## `onlinejudge_command.log_formatter.LogFormatter` · *class*

## Summary:
A custom logging formatter that enhances log message presentation with colored output and semantic prefix handling.

## Description:
The LogFormatter class extends Python's standard logging.Formatter to provide enhanced formatting capabilities for log messages. It adds color coding to log levels and special handling for common log prefixes (like ERROR:, WARNING:) to provide better visual distinction in console output. This formatter is designed to improve readability of log messages in terminal environments by applying appropriate coloring and structural formatting.

## State:
- Inherits from logging.Formatter
- References external constants `log_colors_level` and `log_colors_semantics` (not defined in this file)
- Uses standard logging.Formatter attributes for formatting configuration

## Lifecycle:
- Creation: Instantiate with optional datefmt parameter to control timestamp format
- Usage: Called automatically by Python's logging system when formatting log records
- Destruction: No special cleanup required; relies on parent class behavior

## Method Map:
```mermaid
graph TD
    A[LogFormatter.__init__] --> B[logging.Formatter.__init__]
    A --> C[Set format string]
    B --> D[Initialize base formatter]
    C --> D
    E[LogFormatter.format] --> F[Check levelno against log_colors_level]
    F --> G{levelno in log_colors_level?}
    G -->|No| H[super().format(record)]
    G -->|Yes| I[Process message for heading]
    I --> J[Check for empty message]
    J --> K{Empty message?}
    K -->|Yes| L[heading = '']
    K -->|No| M[Check for semantic prefixes]
    M --> N{Semantic prefix found?}
    N -->|Yes| O[Set heading from log_colors_semantics]
    N -->|No| P[Set heading from log_colors_level]
    P --> Q[Handle exception info]
    Q --> R[Format final message]
    R --> S[Return formatted message]
```

## Raises:
- No explicit exceptions raised by __init__
- May raise exceptions from parent logging.Formatter.__init__ if invalid parameters are passed

## Example:
```python
import logging
from onlinejudge_command.log_formatter import LogFormatter

# Create logger with custom formatter
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
Initializes a log formatter with a standardized format that displays log level and message.

## Description:
Configures the logger to display messages in the format "[LEVEL] message" where LEVEL represents the log severity level and message contains the actual log content. This method sets up a custom logging format while preserving the ability to customize date formatting through the datefmt parameter.

## Args:
    datefmt (Optional[str]): Format string for timestamps. Defaults to None, which uses the default date format.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: Initializes the parent class state with the configured format and datefmt.

## Constraints:
    Preconditions: None
    Postconditions: The instance is properly initialized with the specified logging format.

## Side Effects:
    None: This method performs no I/O operations or external service calls.

### `onlinejudge_command.log_formatter.LogFormatter.format` · *method*

## Summary:
Formats log records with color-coded headings based on log level and message semantics, with fallback to standard formatting.

## Description:
This method customizes the formatting of log records by applying color codes to log messages based on their severity level and semantic prefixes. It implements a multi-step process to determine appropriate coloring:
1. If the log level is not in the supported color mappings, it falls back to standard formatting
2. Otherwise, it determines a heading color based on semantic prefixes or log level
3. It processes exception information if present
4. It returns the formatted message with appropriate color codes

## Args:
    record (logging.LogRecord): The log record to format

## Returns:
    str: The formatted log message string. May include color codes or fall back to standard formatting.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - log_colors_level (module-level dictionary mapping log levels to color codes)
    - log_colors_semantics (module-level dictionary mapping semantic prefixes to color codes)

## Constraints:
    Preconditions:
    - record must be a valid logging.LogRecord instance
    - log_colors_level and log_colors_semantics must be properly initialized module-level dictionaries
    
    Postconditions:
    - When log level is supported, returns a formatted string with color codes
    - When log level is not supported, returns result from parent class formatting
    - Exception information is properly appended when present

## Side Effects:
    None directly, but may cause I/O through inherited logging.Formatter behavior

