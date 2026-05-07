# `log_formatter.py`

## `onlinejudge_command.log_formatter.LogFormatter` · *class*

## Summary:
A logging.Formatter subclass that converts LogRecord level numbers and optional semantic message prefixes into a reusable heading (often containing color escape codes) and returns the formatted message string.

## Description:
LogFormatter replaces the default bracketed level prefix for configured log levels with a configurable "heading" string selected from module-level mappings. It is intended for CLI applications that want concise, optionally colorized log output and simple semantic prefixes (for example, "HTTP: 200 OK" -> "HTTP: 200 OK" with a cyan "HTTP: " heading and "200 OK" message).

Where to instantiate
- Attach an instance to a logging.Handler (e.g., StreamHandler) via handler.setFormatter(LogFormatter()).
- Typical callers: command-line entrypoints, setup code that configures logging for a console-based application.

Why this abstraction exists
- Separates presentation (heading selection and optional color markup) from logging emission.
- Provides semantics-based heading overrides (via message prefixes) and allows level-based headings when no semantic prefix applies.
- Delegates full formatting (timestamp, level name, etc.) to the base logging.Formatter when a record's level is not configured.

## State:
Instance attributes
- Inherited from logging.Formatter. This class does not add new instance attributes.
- The instance is initialized with fmt set to the literal string: '[%(levelname)s] %(message)s', and datefmt is passed through from the constructor argument.

Constructor parameters
- datefmt: Optional[str] = None
    - Passed unchanged to logging.Formatter.__init__ as the datefmt parameter. Accepts None or a format string supported by logging.

Module-level dependencies (must be defined in the same module)
- log_colors_level: Dict[int, str]
    - Keys: logging level numbers (e.g., logging.DEBUG, logging.INFO).
    - Values: heading strings (may include ANSI/colorama escape codes). A falsy value (e.g., '') indicates "no heading" — the formatted output will be the message only.
    - Contract: membership test (levelno in log_colors_level) and indexing (log_colors_level[levelno]) must be supported.
- log_colors_semantics: Dict[str, str]
    - Keys: semantic keywords (case-insensitive comparison performed by converting message to upper-case; typical keys are uppercase like 'HTTP').
    - Values: heading strings (same semantic as above).
    - Contract: iteration via items() and indexing must be supported.

Invariants
- The mappings must be mapping-like (supporting "in" and get/index).
- Heading strings returned from these mappings are intended to be concatenated directly with the message; they must therefore be safe strings for terminal output.

## Lifecycle:
Creation
- Instantiate with optional datefmt:
    - formatter = LogFormatter()
    - formatter = LogFormatter(datefmt='%Y-%m-%d %H:%M:%S')

Usage pattern
- Typical flow:
    1. logging system creates a logging.LogRecord and passes it to Handler.format(record).
    2. Handler.format calls LogFormatter.format(record).
    3. LogFormatter.format returns a str which the handler emits.
- No explicit ordering between methods is required; only format() is used at runtime.

Cleanup
- No resources to release. No context manager or close method required.
- If colored headings rely on colorama, initialize colorama (colorama.init()) in application startup; LogFormatter does not call colorama.init().

## Method Map:
graph LR
    LR_LogRecord[logging system produces LogRecord] --> LR_format[LogFormatter.format(record)]
    LR_format --> CheckLevel{record.levelno in log_colors_level?}
    CheckLevel -- No --> BaseFormat[return super().format(record)]
    CheckLevel -- Yes --> GetMessage[get message = record.getMessage()]
    GetMessage --> EmptyAndNoExc{message is falsy and record.exc_info is None?}
    EmptyAndNoExc -- Yes --> SetHeadingEmpty[heading = '']
    EmptyAndNoExc -- No --> TrySemantics[for key,value in log_colors_semantics.items(): if message.upper().startswith(key+':') -> heading=value; message = message[len(key+':'):].lstrip(); break]
    TrySemantics --> HeadingFromLevelIfNone{if heading is None: heading = log_colors_level[record.levelno]}
    HeadingFromLevelIfNone --> AppendExceptionIfAny{if record.exc_info is not None: message += '\n' + self.formatException(record.exc_info)}
    AppendExceptionIfAny --> ReturnDecision{if not heading: return message else return heading + message}

## Detailed behavior (format)
Signatures
- __init__(self, datefmt: Optional[str] = None) -> None
    - Sets fmt to '[%(levelname)s] %(message)s' and passes datefmt to the base class.
- format(self, record: logging.LogRecord) -> str
    - Accepts a standard LogRecord and returns a formatted string.

Step-by-step behavior
1. If record.levelno is not present in log_colors_level (using membership test "in"), call and return logging.Formatter.format(record). This uses the format string '[%(levelname)s] %(message)s' and the provided datefmt.
2. Otherwise:
   a. Initialize local variable heading = None.
   b. Obtain message = record.getMessage() (this applies any %-formatting from record.args).
   c. If message is falsy (empty string or other falsy value) and record.exc_info is None, set heading = '' (explicit empty heading). This produces output with no heading and no leading newline unless exc_info later appended.
   d. If heading is still None, iterate through log_colors_semantics.items() in iteration order:
       - For each key (string) and value (heading string), check if message.upper().startswith(key + ':').
       - If matched, set heading = value. Then remove the matched prefix from the original message by slicing off len(key + ':') characters and left-stripping whitespace from the remainder: message = message[len(key + ':'):].lstrip(). Break the loop (first match wins).
   e. If heading is still None after semantics scan, set heading = log_colors_level[record.levelno].
   f. If record.exc_info is not None, append '\n' + self.formatException(record.exc_info) to message (this formats the exception trace using the base class method).
   g. If heading is falsy (for example, empty string ''), return message (which may include the appended exception). Otherwise return heading + message (simple concatenation; no extra separator inserted).
   
Edge cases and exact behaviors
- Semantics matching is case-insensitive because message is upper-cased for comparison. The stored key is not upper-cased by the formatter; keys should be provided in a consistent form (commonly uppercase).
- The presence of exc_info when message is empty leads to heading selection via semantics or level mapping (heading is not forced empty in that case), and the exception text will be appended on a new line to the message.
- If a semantics key is found, the colon following the key plus any immediately following whitespace is removed from the returned message.
- If log_colors_level contains a falsy value (e.g., ''), that indicates "suppress heading" and the returned string will be just the message (plus exception).
- If the module-level mappings are missing or have incompatible types, runtime exceptions (TypeError, KeyError, AttributeError) can occur.

## Raises:
- __init__:
    - No explicit raises in this class; invalid datefmt types may be propagated from logging.Formatter.__init__.
- format:
    - May raise:
        - KeyError or TypeError if log_colors_level/log_colors_semantics are not defined or are not mapping-like.
        - Any exceptions propagated from record.getMessage() (if record.msg or record.args are problematic) or from self.formatException if exc_info is malformed.
    - The formatter itself does not catch these exceptions.

## Example:
Assume module-level mappings:
    import logging, colorama
    colorama.init()

    log_colors_level = {
        logging.DEBUG: '',
        logging.INFO: colorama.Fore.GREEN + 'INFO: ' + colorama.Style.RESET_ALL,
        logging.WARNING: colorama.Fore.YELLOW + 'WARNING: ' + colorama.Style.RESET_ALL,
        logging.ERROR: colorama.Fore.RED + 'ERROR: ' + colorama.Style.RESET_ALL,
    }
    log_colors_semantics = {
        'HTTP': colorama.Fore.CYAN + 'HTTP: ' + colorama.Style.RESET_ALL,
        'DB': colorama.Fore.MAGENTA + 'DB: ' + colorama.Style.RESET_ALL,
    }

Usage:
    handler = logging.StreamHandler()
    handler.setFormatter(LogFormatter(datefmt=None))
    logger = logging.getLogger('app')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    logger.info('Hello world')
    # Outputs: "<green INFO: ><reset>Hello world"

    logger.info('HTTP: 200 OK')
    # Semantics 'HTTP' matches: output header is 'HTTP: ' (cyan), message becomes '200 OK'

    logger.debug('')  # DEBUG maps to empty heading
    # Outputs: "" (empty string) unless exc_info provided

### `onlinejudge_command.log_formatter.LogFormatter.__init__` · *method*

## Summary:
Initializes the formatter to use a concise default format for console output and forwards an optional date format to the logging.Formatter base class, thereby configuring the instance's formatting behavior.

## Description:
This constructor sets the logging format string to a fixed, concise pattern and delegates further initialization to logging.Formatter.

Known callers and contexts:
- Instantiated when configuring logging for CLI applications, typically during application startup or in command entrypoints.
- Typical usage: create an instance and attach it to a handler (e.g., handler.setFormatter(LogFormatter())) as part of logger/handler setup.
- It is invoked at the creation lifecycle stage for the formatter, before any calls to LogFormatter.format(record).

Why this is a separate method:
- Encapsulates the choice of the concise format string ('[%(levelname)s] %(message)s') in one place so all LogFormatter instances share consistent presentation.
- Keeps format configuration centralized and distinct from runtime formatting logic implemented in format(), avoiding inlining format string selection where handlers are configured.

## Args:
    datefmt (Optional[str]): Optional date/time format string passed through to logging.Formatter.__init__.
        - Allowed values: None or any format string accepted by the standard logging.Formatter datefmt parameter (typically strftime-compatible).
        - Default: None

## Returns:
    None

## Raises:
    Any exception raised by logging.Formatter.__init__ may propagate unchanged.
    - Example: TypeError if the base class rejects the provided arguments (rare for the passed types).
    - This constructor does not explicitly raise its own exceptions.

## State Changes:
Attributes READ:
    - None in this implementation (no self.<attr> fields are inspected before initialization).

Attributes WRITTEN:
    - The format configuration of the instance is set to the literal '[%(levelname)s] %(message)s' by passing fmt to the base class.
    - The provided datefmt value is forwarded to the base class so that the logging.Formatter-managed date/format state is initialized accordingly.
    - Note: exact attribute names are managed by logging.Formatter (internal formatter state); this constructor does not create new LogFormatter-specific attributes.

## Constraints:
Preconditions:
    - The caller should pass either None or a string as datefmt. Other types may be accepted or rejected by logging.Formatter.__init__ and thus may raise.
    - Module-level invariants expected by the class (e.g., availability of log_colors_level/log_colors_semantics for runtime formatting) are not required at construction time but are required later when format() is called.

Postconditions:
    - After return, the instance is initialized via logging.Formatter.__init__ with:
        - fmt set to '[%(levelname)s] %(message)s'
        - datefmt set to the provided value (or None)
    - The formatter is ready to be attached to a logging.Handler and used to format LogRecord objects.

## Side Effects:
    - Calls logging.Formatter.__init__(fmt=..., datefmt=...), which initializes the base-class formatting machinery. No I/O is performed by this constructor itself.
    - No calls to colorama or other external services are made here.

### `onlinejudge_command.log_formatter.LogFormatter.format` · *method*

## Summary:
Format a logging.LogRecord into a string that optionally prefixes the message with a semantic/color heading based on the record level or message prefix; if the record's level is not handled by this formatter, delegate to the parent implementation. This method does not mutate the formatter's state.

## Description:
This method is invoked by the Python logging framework during record emission (e.g., when a Handler calls its formatter via Handler.format or when a handler directly calls this formatter). Typical lifecycle: a LogRecord is created by logging calls (logger.info/warning/error/etc.), a Handler receives it and asks this Formatter to produce the final text to emit.

The logic is separated into its own method because it customizes formatting behavior beyond the default logging.Formatter: it applies semantic/colored "headings" derived from either a per-level mapping or from message-prefix semantics. Keeping this logic in format (overriding the base implementation) centralizes message->heading resolution and exception formatting, making the behavior reusable by any handler that attaches this formatter.

## Args:
    record (logging.LogRecord): The log record to format. Must expose:
        - levelno (int): numeric logging level used to look up default headings.
        - getMessage() -> str: returns the log message string.
        - exc_info: either None or a (type,value,traceback) tuple; if present, its formatted exception text is appended.

## Returns:
    str: The formatted textual representation of the record.
    Possible return forms:
      - If record.levelno is not a key in the module-level mapping log_colors_level:
          returns the result of calling the base implementation (super().format(record)).
      - Otherwise, one of:
          * message (possibly empty or containing appended formatted exception text) when the resolved heading is falsy (empty string).
          * heading + message when the resolved heading is truthy (non-empty). heading is taken from either:
              - log_colors_semantics when the message begins with a recognized semantic prefix (case-insensitive, matched as KEY + ':'), or
              - log_colors_level[record.levelno] as a fallback.
    Edge cases:
      - If the original message is empty and exc_info is None, heading is set to the empty string; the method will return message (empty string).
      - If exc_info is provided, the textual exception produced by self.formatException(record.exc_info) is appended to the message separated by a newline before heading logic returns the final string.

## Raises:
    Any exception raised by:
      - super().format(record) when record.levelno is not handled (these exceptions propagate).
      - self.formatException(record.exc_info) when exc_info is present (these exceptions propagate).
    The method itself does not explicitly raise its own custom exceptions.

## State Changes:
    Attributes READ:
      - This method calls self.formatException(...) and calls super().format(...). It does not read or depend on any instance attributes set on self (no self.<attr> data fields are read).
    Attributes WRITTEN:
      - None. The method does not modify any self.<attr> fields.

## Constraints:
    Preconditions:
      - record must be a logging.LogRecord with levelno and getMessage present (true for records produced by the stdlib logging module).
      - The module-level mappings log_colors_level and log_colors_semantics must be present and behave like:
          * log_colors_level: mapping from int (levelno) to str (heading prefix).
          * log_colors_semantics: mapping from str (semantic key) to str (heading prefix).
      - If these mappings are missing or mis-typed, KeyError or other exceptions may occur when accessed.

    Postconditions:
      - The method returns a string suitable for emission by a logging.Handler; it does not change the formatter state.
      - If record.levelno was not present in log_colors_level, the returned string equals super().format(record).
      - If exc_info was provided, the returned string contains the formatted exception text appended to the message separated by a single newline.

## Side Effects:
    - No I/O is performed by this method.
    - No external services are called.
    - No mutation of objects outside self is performed (message modifications are local variables).
    - The only observable external calls are calls into the base class Formatter (super().format) and Formatter.formatException which may themselves perform operations (but this method does not directly perform I/O).

