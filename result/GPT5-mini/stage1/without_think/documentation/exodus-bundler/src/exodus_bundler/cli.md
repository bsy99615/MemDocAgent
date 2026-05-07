# `cli.py`

## `src.exodus_bundler.cli.parse_args` · *function*

## Summary:
Parses the exodus bundler command-line arguments and returns the parsed values as a plain dictionary.

## Description:
Constructs an argparse.ArgumentParser configured for the exodus bundler CLI, registers all positional and optional arguments (with their flags, behaviors and defaults), runs the parser on the provided args (or sys.argv when args is None), and returns the parser results converted from argparse.Namespace to a dict via vars(...).

Typical caller:
- A program startup routine or CLI entrypoint that needs a normalized dictionary of options to drive subsequent bundling logic. This function is intentionally focused only on argument definition and parsing; downstream validation or cross-option checks are expected to occur after it returns.

Reason for extraction:
- Isolates argument parsing from program logic to enable straightforward unit testing and to keep argument definitions in a single, maintainable location.

## Args:
    args (list[str] | None):
        Sequence of command-line tokens to parse (excluding program name). If None, the underlying argparse parser reads from sys.argv[1:].

    namespace (argparse.Namespace | None):
        Optional Namespace instance to populate. If None, argparse constructs a new Namespace.

Notes:
- Both parameters are passed directly to parser.parse_args(args, namespace) and are not otherwise validated inside this function.

## Returns:
A dict (result of vars(parser.parse_args(args, namespace))) with these keys and value types:

    executables -> list[str]
        Positional required argument (metavar 'EXECUTABLE', nargs='+'). Must contain one or more values; if absent, argparse will print usage and raise SystemExit.

    chroot -> str | None
        Value from -c / --chroot. Default: None.

    add -> list[str]
        Values from -a / --add / --additional-file. Each occurrence appends a string. Default: [] (empty list).

    detect -> bool
        True if -d / --detect present, else False. (action='store_true')

    no_symlink -> list[str]
        Values from --no-symlink. Each occurrence appends a string. Default: [].

    output -> str | None
        Value from -o / --output. Default: None.

    quiet -> bool
        True if -q / --quiet present, else False.

    rename -> list[str | None]
        Values from -r / --rename. Because of nargs='?' combined with action='append':
            - If the option is supplied with an argument (e.g., -r newname), the appended entry is that string.
            - If the option is supplied without an argument (e.g., -r immediately followed by another option or end of args), the appended entry is None.
        Default: [] (empty list).
        Caller must interpret None entries and enforce any relation between rename entries and executables.

    shell_launchers -> bool
        True if --shell-launchers present, else False.

    tarball -> bool
        True if -t / --tarball present, else False.

    verbose -> bool
        True if -v / --verbose present, else False.

Implementation notes about keys:
- Hyphenated option names are converted to underscore keys in the dict (e.g., --no-symlink -> "no_symlink", --shell-launchers -> "shell_launchers"). The key names directly reflect argparse's dest naming derived from the long option strings and positional name.

## Raises:
    SystemExit
        Raised by argparse.parser.parse_args under these conditions:
            - User requests help (-h/--help): argparse prints help (to stdout) and calls sys.exit(0) -> SystemExit(0).
            - Parsing error (missing required positional, invalid option usage, etc.): argparse prints an error message (to stderr) and calls sys.exit(2) -> SystemExit(2).
        This function does not catch or translate SystemExit; callers that must avoid process exit should catch SystemExit around this call.

## Constraints:
Preconditions:
- args, if supplied, must be an iterable of strings suitable for argparse (typically list[str]). Supplying a non-iterable or non-string tokens will cause argparse to raise an error or behave unexpectedly.
- The function does not validate cross-argument constraints (for example, it does not ensure the number of rename entries matches the number of executables).

Postconditions:
- On successful parse, returns a dict with the exact keys and types listed above.
- No further mutations of global state are performed by this function.

## Side Effects:
- Writes to stdout (help text) and/or stderr (parsing error messages) via argparse.
- May trigger sys.exit (raising SystemExit) as described in Raises.
- No file, network, or persistent-state side effects.

## Control Flow:
flowchart TD
    Start[Start parse_args] --> Create[Create ArgumentParser with defaults formatter]
    Create --> AddPos[Add positional: executables (nargs='+')]
    AddPos --> AddOpts1[Add options: chroot, add (append), detect (store_true)]
    AddOpts1 --> AddOpts2[Add options: no-symlink (append), output, quiet]
    AddOpts2 --> AddOpts3[Add options: rename (nargs='?', append), shell-launchers]
    AddOpts3 --> AddOpts4[Add options: tarball, verbose]
    AddOpts4 --> Parse[Call parser.parse_args(args, namespace)]
    Parse --> Decision{Parsing result}
    Decision -->|Success| Return[Return vars(namespace) as dict]
    Decision -->|Help requested| HelpOut[Print help to stdout -> SystemExit(0)]
    Decision -->|Parse error| ErrorOut[Print error to stderr -> SystemExit(2)]

## Examples:
- Typical programmatic invocation (simulate CLI tokens):
    result = parse_args(['./bin/myapp', '-o', 'bundle.sh', '-a', '/usr/lib/libextra.so', '--tarball'])
    # result is a dict:
    # {
    #   "executables": ["./bin/myapp"],
    #   "chroot": None,
    #   "add": ["/usr/lib/libextra.so"],
    #   "detect": False,
    #   "no_symlink": [],
    #   "output": "bundle.sh",
    #   "quiet": False,
    #   "rename": [],
    #   "shell_launchers": False,
    #   "tarball": True,
    #   "verbose": False
    # }

- Rename option with no argument:
    result = parse_args(['./bin/myapp', '-r'])
    # "rename" will be [None] — callers should interpret None as "flag present but no name supplied".

- Missing required positional:
    # parse_args([]) will cause argparse to print usage to stderr and raise SystemExit(2).

## `src.exodus_bundler.cli.configure_logging` · *function*

## Summary:
Configure the global logger used by the package by setting its log level and attaching two stream handlers: one that routes warnings and errors to stderr with a prefixed level name, and (unless suppressed) one that routes info/debug messages to stdout with plain messages.

## Description:
This function centralizes CLI-oriented logging setup for the package. It:
- Determines an appropriate base log level from the boolean flags (quiet/verbose).
- Ensures messages of WARNING and ERROR levels are emitted to sys.stderr with a "LEVEL: message" prefix.
- Unless suppress_stdout is True, ensures DEBUG and INFO messages are emitted to sys.stdout with plain message text.

Known callers within the provided context:
- Not determinable from the snippet alone. Typical caller: a CLI entrypoint or main function that parses command-line flags and then calls this function to initialize process logging before other work begins.

Why this logic is extracted into its own function:
- Responsibility separation: isolates CLI logging policy and handler configuration from command execution and argument parsing.
- Reusability: allows consistent logging behavior across all CLI commands and tests that simulate CLI runs.
- Testability: logging configuration can be set up or replaced in unit tests without inlining behavior into the main CLI flow.

## Args:
    quiet (bool): If True and verbose is False, prefer only ERROR-level output (suppresses warnings/info/debug). If both quiet and verbose are True, they cancel and default WARN is used.
    verbose (bool): If True and quiet is False, prefer INFO-level output (enables info/debug visibility). If both True, they cancel and default WARN is used.
    suppress_stdout (bool, optional): Defaults to False. When True, the function does not attach the stdout handler (INFO/DEBUG); stderr handler (WARN/ERROR) and level configuration still occur.

Interdependencies:
    - quiet and verbose are mutually influencing: the function only applies the ERROR level when quiet is True and verbose is False, and only applies the INFO level when verbose is True and quiet is False. When both are False or both True, the log level remains at the default WARNING.

## Returns:
    None

The function performs configuration side effects on the package root logger and returns no value.

## Raises:
    This function does not raise any explicit exceptions in the provided implementation.
    Possible runtime exceptions (not raised deliberately) include:
    - AttributeError if exodus_bundler.root_logger is not a logging.Logger-like object with setLevel/addHandler methods.
    - Any I/O or runtime error raised by stream handlers obtained from sys.stdout/sys.stderr (rare in normal environments).

## Constraints:
Preconditions:
    - exodus_bundler.root_logger must exist and behave like an instance of logging.Logger.
    - sys.stdout and sys.stderr must be available file-like stream objects (standard in normal CLI environments).

Postconditions:
    - exodus_bundler.root_logger.level is set to one of: logging.ERROR, logging.INFO, or logging.WARN (the default when neither quiet nor verbose wins).
    - A StreamHandler that filters for WARNING and ERROR and formats messages as "LEVEL: message" is attached to root_logger.
    - If suppress_stdout is False, a StreamHandler that filters for DEBUG and INFO and formats messages as "message" is attached to root_logger.
    - Repeated calls will add additional handlers (the function is not idempotent); duplicate handlers may cause duplicate log output unless the caller ensures idempotency.

## Side Effects:
    - Mutates global logger state: sets level on exodus_bundler.root_logger and adds one or two handlers to it.
    - Emits to stdout and stderr indirectly when logging events occur (no immediate I/O at configuration time).
    - No network or file system access is performed by this function itself.

## Control Flow:
flowchart TD
    Start --> SetDefault[Set log_level = WARNING]
    SetDefault --> CheckQuietVerbose{quiet and not verbose?}
    CheckQuietVerbose -- yes --> SetError[log_level = ERROR]
    CheckQuietVerbose -- no --> CheckVerbose{verbose and not quiet?}
    CheckVerbose -- yes --> SetInfo[log_level = INFO]
    CheckVerbose -- no --> KeepDefault[Keep WARNING]
    SetError --> ApplyLevel
    SetInfo --> ApplyLevel
    KeepDefault --> ApplyLevel
    ApplyLevel --> CreateStderrFilter[Create StderrFilter allowing WARN/ERROR]
    CreateStderrFilter --> AttachStderr[Attach stderr handler with "LEVEL: message" format]
    AttachStderr --> CheckSuppress{suppress_stdout?}
    CheckSuppress -- true --> End[Return]
    CheckSuppress -- false --> CreateStdoutFilter[Create StdoutFilter allowing DEBUG/INFO]
    CreateStdoutFilter --> AttachStdout[Attach stdout handler with "message" format]
    AttachStdout --> End

## Examples:
Example 1 — typical CLI initialization (happy path)
    - Call configure_logging(quiet=False, verbose=True)
    - Effect: root logger level set to INFO; INFO and DEBUG messages (if any) will be printed to stdout without level prefixes; WARNING and ERROR messages will be printed to stderr with an "LEVEL: message" prefix.

Example 2 — quiet mode (only important errors)
    - Call configure_logging(quiet=True, verbose=False)
    - Effect: root logger level set to ERROR; only ERROR messages are routed to stderr. INFO/DEBUG are suppressed by level, and warnings are suppressed because level is ERROR.

Example 3 — suppressing stdout output (only stderr, useful in programs where stdout is used for machine-readable output)
    - Call configure_logging(quiet=False, verbose=False, suppress_stdout=True)
    - Effect: root logger level remains WARNING; stderr handler is attached and will emit WARNING/ERROR messages with level prefixes; no stdout handler is attached so INFO/DEBUG messages — even if emitted — will not be captured by the package handlers.

Notes for implementers:
    - To make this function idempotent in your own implementation, consider checking for and reusing existing handlers with the same type/format/filter before adding new ones.
    - Use logging.WARNING rather than the legacy alias logging.WARN if reproducing this behavior to avoid deprecation warnings in future Python versions.

## `src.exodus_bundler.cli.StderrFilter` · *class*

## Summary:
A stateless logging.Filter that allows only WARNING (logging.WARN) and ERROR level records to pass; intended for attaching to a handler that writes to stderr so that only warnings and errors are emitted there.

## Description:
Use this class when you want to separate log output by severity between handlers (commonly: route WARNING and ERROR to stderr, and route lower severities such as INFO/DEBUG to stdout). Typical call sites create an instance and add it to a stderr-oriented logging.Handler (handler.addFilter(StderrFilter())). This filter enforces the boundary that only records whose level is WARN or ERROR are delivered to the handler it is attached to.

Motivation:
- Keep stderr output limited to warnings and errors so command-line tools present normal informational output on stdout while reporting problems on stderr.
- Provide a simple, reusable abstraction (instead of repeating inline lambda filters) that is clear and testable.

Known callers/factories:
- Any code that configures logging handlers for CLI applications can instantiate and attach this filter to the handler responsible for stderr. (No factory functions are required; the class is constructed directly with no arguments.)

## State:
- This class is stateless (has no instance attributes beyond those provided by the logging.Filter base class).
- There are no __init__ parameters; instantiation requires no arguments.
- Valid values:
  - The filter method expects a logging.LogRecord-like object with an integer attribute levelno.
  - The filter returns True only when record.levelno equals logging.WARN or logging.ERROR.
- Class invariants:
  - Instances do not mutate external state.
  - Repeated calls to filter with equivalent records yield the same boolean result (pure, deterministic behavior).
  - Thread-safety: because the class has no mutable state, it is safe to reuse the same instance across threads.

## Lifecycle:
Creation:
- Instantiate with no arguments: create an instance via StderrFilter().
Usage:
- Attach to a logging.Handler (typically the handler that writes to stderr) via the handler's addFilter method.
- The logging subsystem calls filter(record) for each LogRecord before the handler emits it.
- Typical sequencing:
  1) Configure handlers (one for stdout, one for stderr).
  2) Attach StderrFilter() to the stderr handler.
  3) (Optionally) attach a complementary filter to the stdout handler that rejects WARN/ERROR.
Destruction:
- No explicit cleanup is required. Remove the filter from a handler via handler.removeFilter(instance) if dynamic reconfiguration is needed.
- Not a context manager and has no close/flush responsibilities.

## Method Map:
graph LR
    A[logging subsystem creates LogRecord] --> B[Handler receives record]
    B --> C[StderrFilter.filter(record)]
    C -->|True (WARN or ERROR)| D[Handler emits to stderr]
    C -->|False (other levels)| E[Handler ignores record]

## Methods (behavior reference):
- filter(record)
  - Input: a logging.LogRecord-like object (expected to have attribute levelno: int).
  - Output: bool — True if record.levelno is logging.WARN or logging.ERROR; otherwise False.
  - Side effects: None.
  - Edge cases:
    - If record has no attribute levelno, attribute access will raise AttributeError (this class does not guard against malformed record-like objects).
    - The implementation uses the constants logging.WARN and logging.ERROR; note that logging.WARN is an alias for logging.WARNING in the standard logging module.
  - Typical return semantics:
    - Return True for WARNING-level and ERROR-level records (these pass through to the attached handler).
    - Return False for DEBUG, INFO, and CRITICAL (or CRITICAL will be False unless it equals ERROR numerically; in the standard levels, CRITICAL > ERROR and thus will be filtered out — attachers should consider whether CRITICAL should be included).

## Raises:
- __init__: does not raise (no parameters).
- filter:
  - AttributeError if the provided record object does not have a levelno attribute.
  - No other exceptions are raised by the filter logic itself.

## Example:
- Instantiate the filter:
  - Create an instance: StderrFilter()
- Attach it to a handler that writes to stderr:
  - Call the handler's addFilter method with the StderrFilter instance.
- Resulting behavior:
  - When the logging system emits a LogRecord, the stderr handler will only emit records where levelno is WARNING (logging.WARN) or ERROR (logging.ERROR).
- Complementary configuration:
  - Add a filter to the stdout handler to exclude WARNING and ERROR so that stdout only carries INFO/DEBUG messages.

### `src.exodus_bundler.cli.StderrFilter.filter` · *method*

## Summary:
Allows only warning- and error-level logging records to pass the filter; returns a boolean used by the logging subsystem and does not modify object state.

## Description:
This method is the filtering predicate for a logging.Filter subclass. When invoked by the Python logging framework (e.g., when a Filter is attached to a Logger or Handler), it examines the incoming logging record and permits only records whose level is either WARNING (logging.WARN) or ERROR (logging.ERROR). No repository call-sites were observed for this method; its intended use is to be attached to handlers that direct messages to standard error so that only warnings and errors are emitted to that destination.

This logic is placed in its own method as required by the logging.Filter API (the logging system calls filter(record)) and to keep the decision logic isolated, testable, and easy to reuse or replace (e.g., different filters for different handlers).

## Args:
    record (logging.LogRecord or any object with attribute 'levelno'): The logging record presented by the logging framework. The method expects this object to have an integer-like attribute named levelno representing the log severity.

## Returns:
    bool: True if the record.levelno equals logging.WARN or logging.ERROR; False otherwise.
    - Typical True returns: records whose level is WARNING (alias logging.WARN) or ERROR.
    - Typical False returns: DEBUG, INFO, CRITICAL, or any other level values not equal to WARN or ERROR.

## Raises:
    AttributeError: If the provided record object does not have a 'levelno' attribute.
    TypeError (possible): If record.levelno exists but is of a type that does not support equality comparison to the logging constants (very unlikely for standard LogRecord objects).

## State Changes:
    Attributes READ:
        - None on self: the method does not access any self.<attr> attributes.
        - Reads only the passed-in parameter 'record' (specifically record.levelno).
    Attributes WRITTEN:
        - None: the method does not modify self or the record.

## Constraints:
    Preconditions:
        - The caller must pass an object with a numeric/int-like attribute named levelno (the standard logging.LogRecord satisfies this).
        - This method is intended to be called by the logging framework via the Filter API; calling it outside that context is allowed but callers must supply an appropriate record object.
    Postconditions:
        - The method returns True exactly when record.levelno is equal to logging.WARN or logging.ERROR; otherwise it returns False.
        - No side effects on the filter instance or the record.

## Side Effects:
    - None: no I/O, no external service calls, no mutation of objects outside the scope of the call.

## Implementation notes (for reimplementation):
    - Use the logging module's constants: compare record.levelno to logging.WARN and logging.ERROR.
    - Keep the function body minimal: return record.levelno in (logging.WARN, logging.ERROR)
    - Ensure callers supply a logging.LogRecord or equivalent; defensive callers may catch AttributeError if they accept arbitrary objects.

## `src.exodus_bundler.cli.StdoutFilter` · *class*

## Summary:
A minimal, stateless logging.Filter that permits only DEBUG and INFO LogRecord objects to pass so they can be emitted by a stdout-oriented logging.Handler.

## Description:
StdoutFilter decides whether an incoming logging.LogRecord should be handled by a stdout-targeted handler by accepting only records whose numeric level equals logging.DEBUG or logging.INFO. It is intended to be attached to StreamHandler(sys.stdout) (or similar handlers) to keep informational and debugging output on stdout while higher-severity messages are routed elsewhere (for example, to stderr).

Note about repository usage:
- The module that defines this class also contains a CLI logging configuration function which defines an identical local StdoutFilter class for its handler setup. That local class is what the CLI configuration uses; the top-level StdoutFilter class is provided as a reusable, public filtering utility for other code to instantiate and attach when needed.

Responsibility and boundary:
- Responsibility: accept or reject LogRecord objects based solely on record.levelno.
- Boundary: it does not format, emit, or modify records; it performs no I/O.

## State:
- Attributes: None declared. StdoutFilter is effectively stateless and relies on logging.Filter base behavior.
- For __init__: there are no parameters and no stored state.
- Valid input expectations:
    - The logging framework supplies a logging.LogRecord with an integer attribute levelno.
- Invariants:
    - For any given LogRecord, filter(record) is deterministic and side-effect free.
    - Multiple instances are interchangeable; no per-instance data influences behavior.

## Lifecycle:
Creation:
- Instantiate with no arguments: StdoutFilter()
- No factory functions are required.
Usage:
1. Create or obtain a logging.Handler that writes to stdout (e.g., logging.StreamHandler(sys.stdout)).
2. Optionally set a logging.Formatter on the handler.
3. Attach an instance of StdoutFilter via handler.addFilter(StdoutFilter()).
4. Add the handler to a logger (for example, the application root logger).
5. During logging, the logging subsystem calls filter(record) for each record before the handler emits it; a True return allows emission, False prevents it for that handler.
Ordering:
- There is no required ordering between filters; the logging module evaluates handler filters as part of its emission flow.
Destruction:
- No explicit cleanup is required. To stop using the filter, call handler.removeFilter(filter_instance) or remove the handler from the logger. Instances are garbage-collected normally.

## Method Map:
flowchart LR
    A[Logger creates LogRecord]
    B[Handler receives LogRecord]
    C[StdoutFilter.filter(record)]
    D{record.levelno == DEBUG or INFO?}
    E[Handler emits to stdout]
    F[Handler ignores record]
    A --> B --> C --> D
    D -- yes --> E
    D -- no --> F

## Component details (filter):
- Signature: filter(self, record)
- Inputs:
    - record: logging.LogRecord (expected). The method reads record.levelno (int).
- Returns:
    - bool: True if the record should be processed by the handler (allowed through), False otherwise.
- Behavior:
    - Returns True iff record.levelno is logging.DEBUG or logging.INFO.
    - Returns False for other levels including logging.WARNING, logging.ERROR, logging.CRITICAL, and any custom levels with other numeric values.
- Edge cases and constraints:
    - If record does not have attribute levelno (not a standard logging.LogRecord), accessing record.levelno will raise AttributeError.
    - No conversion or fallback logic for non-integer levelno values is performed.
    - Custom logging levels that numerically match DEBUG or INFO are allowed; others are blocked.
- Side effects:
    - None; the method does not mutate the record or global state.

## Raises:
- StdoutFilter.__init__ does not raise.
- filter may raise AttributeError if record lacks levelno; in typical usage under Python's logging framework this will not occur.

## Example:
- Typical configuration to route info/debug to stdout and warnings/errors to stderr:
  1. Create handlers:
     - stdout_handler = logging.StreamHandler(sys.stdout)
     - stderr_handler = logging.StreamHandler(sys.stderr)
  2. Set formatters and add filters:
     - stdout_handler.setFormatter(logging.Formatter('%(message)s'))
     - stdout_handler.addFilter(StdoutFilter())
     - stderr_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
     - stderr_handler.addFilter(...)  # e.g., a filter that allows WARNING and ERROR
  3. Register handlers:
     - root_logger.addHandler(stdout_handler)
     - root_logger.addHandler(stderr_handler)
  4. Effect:
     - log.debug(...) and log.info(...) are emitted via stdout_handler.
     - log.warning(...), log.error(...), and higher severities are ignored by stdout_handler and should be emitted by stderr_handler.

This class is intentionally small and designed to be composed with complementary handlers/filters to achieve full, severity-based routing of log messages.

### `src.exodus_bundler.cli.StdoutFilter.filter` · *method*

## Summary:
Allows only DEBUG- and INFO-level LogRecord objects to pass this filter; does not modify the object's state.

## Description:
This method evaluates a logging.LogRecord and returns True when the record's level indicates DEBUG or INFO, allowing those records to be emitted by a handler that uses this filter. It is designed to be invoked by the Python logging framework when an instance of StdoutFilter is attached to a logger or handler; it can also be called directly in unit tests.

Why this logic is a separate method:
- Centralizes the rule determining which log levels should be routed to stdout, making it easy to test and change.
- Keeps handler configuration code simple (attach the filter rather than inlining level checks).

Known invocation contexts:
- The Python logging subsystem calls filter(record) on Filter instances attached to handlers during log record processing.
- Tests or custom code may call filter(record) directly to assert behavior.

## Args:
    record (logging.LogRecord): The LogRecord to evaluate. The object must expose an integer `levelno` attribute as provided by the logging module.

## Returns:
    bool: True if record.levelno is logging.DEBUG or logging.INFO; False otherwise.

## Raises:
    AttributeError: If `record` does not have a `levelno` attribute (this will occur because the method accesses record.levelno directly).
    (No other exceptions are raised by this method as implemented.)

## State Changes:
    Attributes READ:
        - None. The method does not read any self.<attr> attributes.
    Attributes WRITTEN:
        - None. The method does not modify self or the record.

## Constraints:
    Preconditions:
        - `record` should be a logging.LogRecord or an object with an integer `levelno` attribute.
    Postconditions:
        - No mutation occurs on self or record.
        - Return value correctly indicates whether the record's level is DEBUG or INFO.

## Side Effects:
    - None. This method performs no I/O, does not call external services, and does not change global logging configuration.

## `src.exodus_bundler.cli.main` · *function*

## Summary:
Orchestrate the CLI run: parse options, set a default output target, configure logging, append any paths read from piped stdin to the add list, and invoke the bundling routine; on a FatalError, log and exit with status 1.

## Description:
This function is the top-level command-line orchestration for the bundler process. Its responsibilities are:
- Obtain a normalized options dictionary by delegating to parse_args(args, namespace).
- Ensure a sensible default for the output option when none is provided:
    - If sys.stdout.isatty() is True, set output to the filename template "./exodus-{{executables}}-bundle.{{extension}}".
    - Otherwise set output to "-" to indicate that the bundle should be written to stdout.
- Remove logging control flags ('quiet' and 'verbose') from the options dict, compute suppress_stdout as args['output'] == '-', and call configure_logging(quiet, verbose, suppress_stdout=suppress_stdout).
- If stdin is not a TTY, read all data from sys.stdin, run extract_paths on that content, and append the returned list of paths to args['add'].
- Call create_bundle(**args) with the remaining keyword arguments.
- Catch FatalError (imported from exodus_bundler.errors), log an error message and the FatalError instance (passing exc_info=verbose to include a traceback when verbose is True), and exit the process with sys.exit(1).

Known callers:
- Intended to be used as the CLI entrypoint (e.g., from a console script or a module-level main guard). Tests that emulate CLI invocation may call main(args=...) directly.

Why extracted:
- Keeps CLI orchestration separate from argument parsing, logging policy, stdin parsing, and the bundling implementation to aid testability and clarity.

## Args:
    args (list[str] | None):
        - Passed through directly to parse_args. If None, parse_args will read from sys.argv[1:].
    namespace (argparse.Namespace | None):
        - Passed through to parse_args; if None parse_args constructs a new Namespace.

Interdependencies and mutation:
- main expects parse_args to return a dictionary and will mutate that dict:
    - It may set args['output'] (if previously None).
    - It will pop 'quiet' and 'verbose' from the dict (these keys are removed and not forwarded to create_bundle).
    - It may extend args['add'] by appending values extracted from stdin.
- After these mutations the remaining keys in args are forwarded as keyword arguments to create_bundle.

## Returns:
    None (implicitly). On normal completion, create_bundle has been invoked and main returns None.
    Non-returning behaviors:
    - main can raise SystemExit:
        * Indirectly via parse_args (argparse raises SystemExit for help or parse errors).
        * Directly via sys.exit(1) when catching FatalError.
    - Other exceptions raised by create_bundle or other called functions are not caught by main and will propagate.

## Raises:
    SystemExit
        - May be raised by parse_args on help or parse errors (not caught by main).
        - main explicitly calls sys.exit(1) when create_bundle raises FatalError, resulting in SystemExit(1).
    FatalError
        - Will not escape main because it is caught; instead main logs and exits.
    KeyError
        - If the dict returned by parse_args is missing expected keys that main directly accesses:
            * Accessing args['output'] or args['add'] will raise KeyError if those keys are absent.
            * args.pop('quiet') or args.pop('verbose') will raise KeyError if those keys are absent.
    TypeError / ValueError / NameError
        - If args['add'] exists but is not a list-like supporting in-place concatenation (args['add'] += list), a TypeError may be raised.
        - If a module-level logging variable named logger is not defined, NameError will occur when main calls logger.error (see Preconditions / Constraints).
    Any other exception propagated from create_bundle or called helpers (e.g., OSError from filesystem operations performed by create_bundle) will propagate unless it is a FatalError (which is caught).

## Constraints:
Preconditions:
    - parse_args must exist and must return a dict containing at minimum the keys:
        * 'output' (str | None)
        * 'add' (list[str])
        * 'quiet' (bool)
        * 'verbose' (bool)
      These types are required because main indexes and mutates these keys directly.
    - sys.stdin and sys.stdout must implement isatty() and read() semantics as used by the function.
    - The module must expose a module-level logger variable named logger that supports logger.error(msg, exc_info=...), or else a NameError will occur when main attempts logging in the FatalError handler. (In many implementations this is bound to exodus_bundler.root_logger or a child logger; main itself does not establish that binding.)
    - configure_logging, extract_paths, and create_bundle must be callable with the semantics described in their respective modules.

Postconditions:
    - On successful completion, create_bundle(**kwargs) has been called with kwargs equal to the parse_args dict after removing 'quiet' and 'verbose', and after setting a default for 'output' and appending any stdin-extracted paths to 'add'.
    - If create_bundle raised FatalError, the process exits with status code 1 (SystemExit(1)) after the error is logged.

## Side Effects:
    - Mutates the parsed args dict returned by parse_args (sets 'output' possibly, pops 'quiet' and 'verbose', extends 'add').
    - Calls configure_logging, which mutates global logging configuration (attaches handlers and sets levels).
    - Reads from sys.stdin when piped, and calls extract_paths on that content.
    - Calls create_bundle(**args) which performs filesystem mutations (creates directories, copies files, creates symlinks) and other side effects described in bundling.create_bundle documentation.
    - On FatalError, logs via the module logger and calls sys.exit(1) to terminate the process.

## Control Flow:
flowchart TD
    Start[Start main] --> ParseArgs[args = parse_args(args, namespace)]
    ParseArgs --> CheckOutput{args['output'] is None?}
    CheckOutput -- yes --> StdoutTTY{sys.stdout.isatty()?}
    StdoutTTY -- true --> SetDefaultOut[args['output'] = "./exodus-{{executables}}-bundle.{{extension}}"]
    StdoutTTY -- false --> SetDash[args['output'] = "-"]
    CheckOutput -- no --> SkipOut
    SetDefaultOut --> AfterOut
    SetDash --> AfterOut
    SkipOut --> AfterOut
    AfterOut --> PopFlags[quiet = args.pop('quiet'); verbose = args.pop('verbose')]
    PopFlags --> Suppress{args['output'] == '-'?}
    Suppress -- true --> ConfigureLoggingTrue[configure_logging(quiet, verbose, suppress_stdout=True)]
    Suppress -- false --> ConfigureLoggingFalse[configure_logging(quiet, verbose, suppress_stdout=False)]
    ConfigureLoggingTrue --> StdinTTY{sys.stdin.isatty()?}
    ConfigureLoggingFalse --> StdinTTY
    StdinTTY -- false --> ReadStdin[content = sys.stdin.read(); additions = extract_paths(content); args['add'] += additions]
    StdinTTY -- true --> SkipRead
    ReadStdin --> TryBundle
    SkipRead --> TryBundle
    TryBundle[try: create_bundle(**args)] -->|Success| End
    TryBundle -->|FatalError| FatalHandler[logger.error("Fatal error encountered, exiting."); logger.error(fatal_error, exc_info=verbose); sys.exit(1)]

## Examples:
1) Basic programmatic run (TTY stdout):
    - Call: main(args=['/usr/bin/myapp', '-o', 'bundle.sh'])
    - parse_args returns a dict with output='bundle.sh', add=[], quiet=False, verbose=False
    - main configures logging with suppress_stdout=False and calls create_bundle(output='bundle.sh', add=[], ...)
    - Returns None on success.

2) Piped input supplying extra files:
    - Command usage: producer | exodus-bundler [options]
    - When main runs with stdin not a TTY, it reads all stdin, extract_paths(content) returns file paths, and main extends args['add'] with those paths before calling create_bundle.

3) Default output when none specified:
    - If parse_args yields output=None and sys.stdout.isatty() is True, main will set output to "./exodus-{{executables}}-bundle.{{extension}}".
    - If parse_args yields output=None and stdout is not a TTY, main will set output to "-" and configure_logging(..., suppress_stdout=True) to avoid emitting INFO/DEBUG to stdout.

4) Error behavior:
    - If create_bundle raises FatalError, main logs a short message and the fatal_error instance. The second log call sets exc_info=verbose (i.e., if verbose was True prior to being popped, the logger is requested to include exception traceback information). main then calls sys.exit(1).

Notes for implementers:
- Be explicit in tests: parse_args may raise SystemExit for help or parse errors; to test main without process exit, call parse_args separately or catch SystemExit in the test harness.
- Ensure parse_args returns the required keys and correct types; otherwise main may raise KeyError or TypeError when attempting to mutate the args dict.
- Provide or bind a module-level logger named logger (for example, "logger = root_logger.getChild(__name__)" or "logger = root_logger") so the FatalError handler can log as implemented.

