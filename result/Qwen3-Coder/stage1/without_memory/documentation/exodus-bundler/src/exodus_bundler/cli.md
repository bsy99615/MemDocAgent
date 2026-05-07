# `cli.py`

## `src.exodus_bundler.cli.parse_args` · *function*

*No documentation generated.*

## `src.exodus_bundler.cli.configure_logging` · *function*

*No documentation generated.*

## `src.exodus_bundler.cli.StderrFilter` · *class*

*No documentation generated.*

### `src.exodus_bundler.cli.StderrFilter.filter` · *method*

## Summary:
Filters log records to only allow WARNING and ERROR level messages to pass through to stderr.

## Description:
This method implements a logging filter that selectively processes log records based on their severity level. It is designed to be used with Python's logging system to route only warning and error messages to stderr while filtering out other log levels like INFO and DEBUG.

## Args:
    record (logging.LogRecord): The log record to be filtered

## Returns:
    bool: True if the record level is either WARNING (30) or ERROR (40), False otherwise

## Raises:
    None: This method does not raise any exceptions

## State Changes:
    Attributes READ: None - This method only reads the record's levelno attribute
    Attributes WRITTEN: None - This method does not modify any instance attributes

## Constraints:
    Preconditions: The record parameter must be a valid logging.LogRecord instance
    Postconditions: The method always returns a boolean value indicating whether the record should be processed

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only evaluates the log record's level.

## `src.exodus_bundler.cli.StdoutFilter` · *class*

*No documentation generated.*

### `src.exodus_bundler.cli.StdoutFilter.filter` · *method*

## Summary:
Filters logging records to permit only DEBUG and INFO level messages to stdout.

## Description:
This method implements a logging filter that controls which log records are output to standard output. It is part of the StdoutFilter class used in the Exodus bundler's logging configuration to separate debug/INFO messages (sent to stdout) from warnings/errors (sent to stderr).

## Args:
    record (logging.LogRecord): The logging record to be filtered

## Returns:
    bool: True if the record's level is either logging.DEBUG or logging.INFO, False otherwise

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The record parameter must be a valid logging.LogRecord instance
    Postconditions: The method always returns a boolean value indicating whether the record should be processed

## Side Effects:
    None

## `src.exodus_bundler.cli.main` · *function*

*No documentation generated.*

