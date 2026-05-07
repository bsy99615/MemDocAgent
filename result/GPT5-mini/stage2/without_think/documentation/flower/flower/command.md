# `command.py`

## `flower.command.sigterm_handler` · *function*

## Summary:
Logs the received POSIX signal and terminates the process with exit code 0.

## Description:
This function is a compact signal handler intended to be registered with the Python signal framework to perform a clean, immediate shutdown when a termination signal is received. When invoked it records the signal and calls the interpreter exit routine.

Known callers within the codebase:
- No direct callers were found in the provided source snippet. Typical usage is to register it with signal.signal, for example during application bootstrap or CLI setup:
  - signal.signal(signal.SIGTERM, sigterm_handler)
  - It may also be registered for other signals (e.g., SIGINT) if the application chooses to treat those signals the same way.

Why this logic is extracted into its own function:
- Keeps signal-handling behavior explicit and testable.
- Separates "what to do on termination" from the code that registers the handler and performs application startup.
- Makes it easy to replace or mock the handler in tests or different deployment scenarios.

## Args:
    signum (int):
        The numeric signal number delivered to the process (e.g., signal.SIGTERM -> typically 15).
    _ (object):
        The second argument is the current stack frame as passed by Python's signal API. This parameter is intentionally unused and ignored.

Notes on arguments:
- The function ignores the frame argument by design; only the numeric signal value is used.
- Both arguments follow the Python signal handler calling convention: handler(signum, frame).

## Returns:
    None
    - This function does not return normally. It calls sys.exit(0), which raises SystemExit. Control does not continue past the call site in the current process; the interpreter exit sequence begins.

## Raises:
    SystemExit
        - Always raised by calling sys.exit(0) when the handler executes. The exit code will be 0.
    (Implicit) Any exceptions raised by logger.info
        - If the module-level logger object is misconfigured or its .info method raises, that exception will propagate instead of SystemExit (this is incidental and not part of the intended normal path).

## Constraints:
Preconditions:
- The function must be invoked via the Python signal dispatch; it is intended to be used as a signal handler. Per Python signal semantics, signals are only delivered to the main thread — therefore the handler will only be invoked in the main thread.
- A module-level logger object named logger must be accessible; the function calls logger.info.

Postconditions:
- A SystemExit is raised with code 0, initiating process termination. atexit handlers and registered cleanup callbacks will be executed as part of Python's shutdown sequence unless the interpreter is forcibly killed.

## Side Effects:
- Logging: emits an informational log entry reporting the received signal and that shutdown is starting (calls logger.info).
- Process termination: invokes sys.exit(0), which raises SystemExit and initiates interpreter shutdown (runs atexit handlers, flushes stdio, etc).
- No file, network, or other I/O is performed directly by this function beyond what the logging framework may do.

## Control Flow:
flowchart TD
    A[Signal delivered -> handler called] --> B{Log signal}
    B --> C[Call logger.info('%s detected, shutting down', signum)]
    C --> D[Call sys.exit(0)]
    D --> E[SystemExit raised -> interpreter shutdown]
    E --> F[atexit handlers run and process exits]

## Examples:
- Register as SIGTERM handler during application bootstrap:
  - signal.signal(signal.SIGTERM, sigterm_handler)

- Testing the handler in isolation (pseudo-usage):
  - Call sigterm_handler(signal.SIGTERM, None) and assert that a SystemExit with code 0 is raised. Wrap the call in a try/except to observe the SystemExit:
    - try:
        sigterm_handler(signal.SIGTERM, None)
      except SystemExit as e:
        assert e.code == 0

- If you want a different exit code or more complex shutdown logic, wrap this handler or register a different function that performs the additional cleanup before calling sys.exit with the desired code.

## `flower.command.flower` · *function*

## Summary:
Bootstraps and starts the Flower web application: applies environment and CLI options, extracts runtime settings, configures logging, instantiates the Flower application, registers shutdown handlers, optionally prints a startup banner, and starts the application event loop.

## Description:
- Known callers:
    - Intended to be invoked by the CLI entrypoint that implements the Flower subcommand (typically a Click command callback). It receives the Click invocation context (ctx) and the subset of argv tokens intended for Tornado/Flower (tornado_argv). The call usually happens during process startup when the user executes something like `celery flower ...` or a dedicated `flower` CLI.
    - In the provided snapshot no explicit call-sites were discovered; treat this function as the central CLI startup action for Flower.

- Typical trigger:
    - After parsing the CLI invocation and before entering the Tornado I/O loop. Called once per process start to configure and launch the Flower HTTP server and its background components.

- Why this logic is extracted:
    - Encapsulates the entire startup sequence and the exact ordering of initialization steps (warn about misplaced Celery args → env options → parse options/config → settings extraction → logging setup → instantiate Flower → shutdown registration → start). This enforces consistent initialization semantics and centralizes side-effects so tests and alternative entrypoints can reuse the same bootstrap behavior without duplication.

## Args:
    ctx (click.Context)
        - The Click command context for the current invocation.
        - Required attributes used by this function:
            * ctx.obj: an object with attributes:
                - app: a Celery application-like object (used only for banner information and passed as capp to Flower).
                - quiet: boolean-like flag; when truthy suppresses printing the startup banner.
        - Preconditions:
            * ctx must be a valid Click Context object whose .obj attribute is set and contains .app and .quiet.
            * If ctx or ctx.obj is missing or malformed, AttributeError will result.

    tornado_argv (Iterable[str])
        - Sequence (usually list) of command-line tokens that were passed to the Flower subcommand and are relevant for Tornado/Flower parsing.
        - Typically derived from sys.argv but pre-filtered to include only Flower/Tornado-recognized options.
        - Preconditions: elements should be strings; non-string elements may cause TypeError or parsing failures in downstream helpers.

## Returns:
    None
    - The function does not return a value. It either:
        * Starts the application's event loop and (normally) blocks/processes until the loop terminates, or
        * Returns after catching KeyboardInterrupt/SystemExit raised during startup as handled by the try/except around flower_app.start().

    - Possible control outcomes:
        * Normal long-running path: flower_app.start() enters the I/O loop and the function does not return until the loop stops.
        * Normal terminal handling: KeyboardInterrupt or SystemExit thrown from start() is caught and suppressed (the function returns).
        * Other exceptions propagate to the caller (see Raises).

## Raises:
    The function itself does not explicitly raise exceptions, but many called helpers can raise; the following are observable and how they can be triggered:

    - AttributeError
        - If ctx or ctx.obj or ctx.obj.app or ctx.obj.quiet are missing.
        - If print_banner/app accessors expect attributes that the provided app object lacks.

    - KeyError
        - Could originate from apply_env_options() (when an environment variable names an unrecognized option) or from extract_settings() if expected keys are missing in the shared settings mapping.

    - ValueError / TypeError
        - Can be raised by apply_env_options() when converting environment variable strings to expected types (e.g., invalid int, invalid boolean string), or by apply_options() / parse_command_line when arguments are malformed.

    - IOError (or OSError on some platforms)
        - apply_options() can raise this when parse_config_file fails to read a user-specified config file. The function does not catch this; it will propagate.

    - SystemExit
        - extract_settings() may call sys.exit(1) on invalid auth configuration; sigterm_handler (registered later) calls sys.exit(0) when a SIGTERM is received. Both raise SystemExit; note that the call to flower_app.start() is wrapped in an except (KeyboardInterrupt, SystemExit) that will catch and suppress SystemExit if it occurs during start().

    - Exceptions from Flower initialization or start:
        - Flower(...) constructor can raise exceptions originating from tornado/celery initialization (e.g., invalid ssl_options, failure importing Celery modules).
        - flower_app.start() can raise network or runtime exceptions (binding sockets, starting the I/O loop). These will propagate unless they are KeyboardInterrupt or SystemExit (which are caught and suppressed).

## Constraints:
- Preconditions (must be true before calling):
    - The Tornado options and any configuration files should be parseable by apply_options; tornado_argv is expected to be suitable for parsing.
    - ctx.obj must exist and contain valid .app (a Celery app object or compatible stub) and .quiet attributes.
    - The module-level helpers (warn_about_celery_args_used_in_flower_command, apply_env_options, apply_options, extract_settings, setup_logging, print_banner, sigterm_handler) and global symbols (options, settings) must be importable and function as expected.

- Postconditions (guarantees after return, when no exception propagates):
    - If start() ran and then returned (normally or because of a KeyboardInterrupt/SystemExit caught by the function), any atexit handlers have been registered (flower_app.stop registered) and the SIGTERM handler is installed.
    - If the start path completed without propagating an exception, the Flower application will have been started (listeners bound, events subsystem started, io_loop running while the function blocked).
    - If the function returns (because start() raised KeyboardInterrupt/SystemExit and was caught), the Flower application may still be running or may have been stopped depending on how the I/O loop and the exception were raised; the function does not guarantee application shutdown here.

## Side Effects:
- Calls warn_about_celery_args_used_in_flower_command(ctx, tornado_argv): may log warnings about misplaced Celery options.
- Calls apply_env_options(): mutates the global tornado.options object by setting attributes based on environment variables.
- Calls apply_options(sys.argv[0], tornado_argv): parses CLI tokens and possibly loads a config file, mutating tornado.options; may attempt to read a file (I/O).
- Calls extract_settings(): mutates the shared settings mapping (imported from urls.settings), possibly calling sys.exit(1) on invalid auth.
- Calls setup_logging(): mutates logging configuration and possibly options.logging.
- Instantiates Flower(capp=app, options=options, **settings): constructs the Tornado web application which:
    - Imports Celery modules, builds executors and inspectors, and prepares background Events; may import modules and allocate resources.
- Registers atexit handler: atexit.register(flower_app.stop) ensures flower_app.stop runs on interpreter shutdown.
- Registers SIGTERM handler: signal.signal(signal.SIGTERM, sigterm_handler) will install a handler that logs the signal and calls sys.exit(0) when SIGTERM is delivered.
- Calls print_banner(app, 'ssl_options' in settings) unless ctx.obj.quiet is truthy: emits startup info via the logger (access URL or unix socket, broker URI, registered tasks, settings dump).
- Calls flower_app.start(): causes side effects of starting the Tornado HTTP server (binding sockets or unix socket), starting background events and I/O loop (blocks current thread until stopped), and creating thread executors.
- Note: network binds, threads, and event loop lifecycle are all created/managed by Flower.start() and Flower.stop().

## Control Flow:
flowchart TD
    Start([Start]) --> Warn["warn_about_celery_args_used_in_flower_command(ctx, tornado_argv)"]
    Warn --> Env["apply_env_options()"]
    Env --> Options["apply_options(sys.argv[0], tornado_argv)"]
    Options --> Settings["extract_settings()"]
    Settings --> Logging["setup_logging()"]
    Logging --> Instantiate["app = ctx.obj.app; flower_app = Flower(capp=app, options=options, **settings)"]
    Instantiate --> RegisterAtexit["atexit.register(flower_app.stop)"]
    RegisterAtexit --> RegisterSignal["signal.signal(SIGTERM, sigterm_handler)"]
    RegisterSignal --> MaybeBanner{"if not ctx.obj.quiet ?"}
    MaybeBanner -- yes --> Banner["print_banner(app, 'ssl_options' in settings)"]
    MaybeBanner -- no --> SkipBanner["(skip banner)"]
    Banner --> StartApp
    SkipBanner --> StartApp
    StartApp["try: flower_app.start()"] --> Running
    Running -->|KeyboardInterrupt or SystemExit raised| Suppress["except (KeyboardInterrupt, SystemExit): pass"]
    Running -->|Other exception raised| Propagate["exception propagates to caller"]
    Suppress --> End([Return None])
    Propagate --> EndWithError([Raises exception])

## Examples:
- Typical CLI wiring (conceptual):
    - A Click command handler obtains ctx (click.Context) and the filtered tornado_argv list and calls:
        flower(ctx, tornado_argv)
      Expected effect: the application will be configured and started (blocking in the I/O loop) until interrupted; on interrupt the function catches KeyboardInterrupt/SystemExit and returns.

- Minimal illustrative startup sequence (pseudocode narrative):
    1. User runs: celery flower --port=5555
    2. CLI code constructs ctx.obj with a Celery app object and quiet=False, computes tornado_argv (Flower-relevant args).
    3. The CLI calls: flower(ctx, tornado_argv)
    4. The function applies env and CLI options, maps options into runtime settings, configures logging, creates the Flower web app, registers cleanup handlers, prints a startup banner (logger.info lines), and then calls flower_app.start() which begins listening and starts the Tornado I/O loop.

- Error handling advice for callers:
    - Surround the call with try/except to handle and report errors that can originate from config parsing (IOError), invalid environment values (ValueError), invalid auth (SystemExit from extract_settings), or unexpected initialization failures from Flower(...) or start(). If you want the process to exit on SystemExit thrown by sigterm_handler, do not run the call inside an except that swallows SystemExit; the current implementation swallows SystemExit only if it occurs during flower_app.start() because of the local try/except.

## `flower.command.apply_env_options` · *function*

## Summary:
Scan environment variables for Flower-prefixed names and apply their values to the Tornado `options` object, converting types according to each option's declared type and multiplicity.

## Description:
This function turns environment variables that represent Flower configuration settings into values assigned on the global Tornado `options` object. It:
- Filters os.environ keys using the predicate that checks for the Flower-specific prefix and membership among known option names (see is_flower_envvar).
- Normalizes the environment variable name by removing the configured prefix once and lowercasing the remainder to produce the option attribute name.
- Looks up option metadata in options._options to determine the target type and whether the option accepts multiple values.
- Converts the environment string value into the proper Python type (including a special boolean parsing path) and assigns it to options.<name>.

Known callers within the codebase:
- No explicit callers were present in the provided source excerpt. Typical usage is during application startup or initialization before the Flower app is created (i.e., a bootstrap step that merges configuration from env vars into Tornado `options` prior to parsing command line or config files).

Why this logic is extracted:
- Centralizes environment-to-option mapping and parsing rules so startup code can simply call this function once instead of re-implementing parsing rules at multiple places.
- Encapsulates normalization, lookup fallback (underscore -> dash), multiplicity handling, and boolean-string semantics in a single, testable place.

## Args:
    None

Note: The function reads global module-level symbols (ENV_VAR_PREFIX, is_flower_envvar) and the Tornado `options` object. These are required to exist and be correctly configured before calling.

## Returns:
    None

The function performs in-place updates on the imported `options` object and does not return a value.

## Raises:
    KeyError
        If the normalized option name (lower-cased remainder after removing the prefix) is not present in options._options, and the fallback with underscores replaced by hyphens is also not present, a KeyError will be raised when attempting to index options._options. This propagates out of the function.

    ValueError
        If an option has type bool and the environment value is not a recognized boolean string, utils.strtobool raises ValueError. The function wraps that result with bool(...), but does not catch the ValueError, so it propagates.

    TypeError or ValueError (from option.type conversions)
        When converting values (single or for each element of a comma-split list) via option.type(value) or option.type(element), the invoked constructor/function may raise TypeError or ValueError for invalid inputs (for example, int('') or float('abc')). Those exceptions are not caught here and will propagate.

    AttributeError / NameError (rare)
        If module-level symbols the function depends on (ENV_VAR_PREFIX, is_flower_envvar, options) are not defined or malformed, attribute access or name resolution could raise NameError or AttributeError before parsing begins.

## Constraints:
Preconditions:
    - ENV_VAR_PREFIX must be defined (string) and consistent with the predicate is_flower_envvar.
    - is_flower_envvar must be available and correctly return True for env var names that should be applied.
    - options must be the Tornado `options` object and must expose an _options mapping containing metadata objects with attributes:
        * type: a callable to convert strings to the option's Python type
        * multiple: a boolean indicating whether the option accepts multiple values
      (The code accesses options._options[name] directly; this is a protected-access requirement.)

Postconditions:
    - For every environment variable that passes is_flower_envvar, a corresponding attribute on the `options` object exists and has been set to the converted value (options.<name>).
    - Values are converted according to option.multiple and option.type rules described below.

## Behavior and value conversion rules (details):
- Name normalization:
    * The env-var name is transformed by removing the first occurrence of ENV_VAR_PREFIX and lowercasing the remainder:
        name = env_var_name.replace(ENV_VAR_PREFIX, '', 1).lower()
    * The normalized name (underscores preserved) is the attribute name used with setattr(options, name, value).

- Option metadata lookup:
    * The function first tries options._options[name].
    * If that fails with KeyError, it retries with name.replace('_', '-') (i.e., convert underscores to hyphens).
    * If both lookups fail, a KeyError propagates.

- Multiplicity:
    * If option.multiple is truthy, the raw environment value is split on commas, and each element is converted via option.type(element).
    * Splitting an empty string yields [''] which will be passed to option.type and may produce an error depending on type.

- Boolean parsing:
    * If option.type is exactly bool, the code uses utils.strtobool(value) which:
        - Accepts (case-insensitive) 'y','yes','t','true','on','1' -> returns 1
        - Accepts 'n','no','f','false','off','0' -> returns 0
        - Raises ValueError otherwise
      The function then wraps the integer result with bool(...), so recognized truthy strings become True, falsy become False.

- Non-boolean single values:
    * For non-bool single-value options, the code calls option.type(value) directly (e.g., int('123') -> 123).

## Side Effects:
    - Mutates the global Tornado `options` object by assigning attributes: setattr(options, name, converted_value).
    - No file, network, or stdout/stderr I/O is performed here.
    - No other global state is mutated by this function.

## Control Flow:
flowchart TD
    Start --> CollectEnv["env_options = filter(is_flower_envvar, os.environ)"]
    CollectEnv --> ForEach["for env_var_name in env_options"]
    ForEach --> NameNorm["name = env_var_name.replace(ENV_VAR_PREFIX,'',1).lower()"]
    NameNorm --> ReadVal["value = os.environ[env_var_name]"]
    ReadVal --> LookupTry1["try: option = options._options[name]"]
    LookupTry1 --> LookupOK1["found -> continue"]
    LookupTry1 --> LookupExcept1["except KeyError -> try fallback"]
    LookupExcept1 --> LookupTry2["option = options._options[name.replace('_','-')]"]
    LookupTry2 --> LookupOK2["found -> continue"]
    LookupTry2 --> LookupExcept2["KeyError -> propagate error"]
    LookupOK1 --> CheckMultiple{"if option.multiple ?"}
    LookupOK2 --> CheckMultiple
    CheckMultiple -- True --> SplitList["value = value.split(',')"]
    SplitList --> ConvertEach["value = [option.type(i) for i in list]"]
    CheckMultiple -- False --> IsBool{"if option.type is bool ?"}
    IsBool -- True --> BoolParse["value = bool(strtobool(value))"]
    IsBool -- False --> TypeConvert["value = option.type(value)"]
    ConvertEach --> SetAttr["setattr(options, name, value)"]
    BoolParse --> SetAttr
    TypeConvert --> SetAttr
    SetAttr --> NextIter["next env var"]
    LookupExcept2 --> ErrorPropagate["raise KeyError -> caller sees exception"]
    ErrorPropagate --> End
    NextIter --> End

## Examples:
Scenario 1 — simple scalar:
    Environment: FLOWER_PORT=5555
    Precondition: options._options contains an entry for 'port' whose type is int and multiple is False.
    Effect: After calling apply_env_options(), options.port is set to integer 5555.

Scenario 2 — boolean parsing:
    Environment: FLOWER_DEBUG=true
    Precondition: options._options['debug'].type is bool.
    Effect: utils.strtobool('true') -> 1; bool(1) -> True. options.debug is True.
    Error case: FLOWER_DEBUG='maybe' -> utils.strtobool('maybe') raises ValueError, which propagates.

Scenario 3 — multiple values:
    Environment: FLOWER_ALLOWED_HOSTS=host1,host2,host3
    Precondition: options._options['allowed_hosts'].multiple is True and type is str (or another type).
    Effect: value becomes ['host1','host2','host3'] (with each element passed through option.type).

Error handling guidance (recommended usage pattern):
    - Call apply_env_options() early in startup. Surround it with a try/except if you want to provide friendlier messages or fallback defaults:
      * Catch KeyError to detect an unrecognized environment-based option name.
      * Catch ValueError/TypeError to detect invalid value formats (e.g., non-integer where int is expected, or unrecognized boolean strings).

## `flower.command.apply_options` · *function*

## Summary:
Filter the provided argv to Flower / Tornado-recognized options, parse those options into the global tornado.options object, attempt to load and apply a configuration file, and then re-parse command-line options so explicit CLI flags override config values.

## Description:
This function is a CLI-startup helper invoked during process initialization to ensure that only Flower/Tornado-managed options are parsed and applied. It performs three main steps: filter input tokens to the subset that map to tornado.options, parse those tokens to set initial option values, attempt to parse a configuration file (if present), and re-parse the same CLI tokens so they take precedence over any config values.

Known callers within the codebase (based on the provided snapshot):
- No explicit callers of apply_options were found in the provided file snapshot. It is intended to be invoked by the Flower CLI / startup entrypoint during early application initialization. The function itself calls is_flower_option (a helper defined in the same module in the snapshot). The is_flower_option helper's documentation states that, in the snapshot, no other direct callers were found elsewhere in the codebase; apply_options is the evident consumer in this context.

Why this is extracted:
- It centralizes the logic for:
  1) recognizing which argv tokens are managed by tornado.options (via is_flower_option),
  2) performing the two-phase parse (CLI → config file → CLI override), and
  3) treating a missing default config file as non-fatal while treating a missing custom config as an error.
  Extracting this behavior avoids duplicating parsing/retry logic across multiple startup paths and makes the precedence semantics explicit.

## Args:
    prog_name (str):
        - The program name used as the first element when calling parse_command_line; typically sys.argv[0] or a CLI subcommand name.
        - Required: must be a string.
    argv (Iterable[str] or list[str]):
        - Sequence of command-line tokens (usually sys.argv[1:]) from which Flower/Tornado options should be extracted.
        - The function filters this sequence using is_flower_option before passing to parse_command_line.
        - Elements are expected to be strings (e.g., '--port=5555', '--url-prefix=/flower'). Non-string elements may raise attribute errors inside the filter predicate.

Notes on parameter interdependencies:
- The behavior depends on the value of the global tornado.options.options.conf (options.conf) at call time: parse_config_file is invoked on os.path.abspath(options.conf).
- DEFAULT_CONFIG_FILE (imported from .options inside the function) is used to decide whether a missing config file is an error (missing custom config) or acceptable (missing default config).

## Returns:
    None
    - The function has no explicit return value; it returns None implicitly.
    - Effect: the global tornado.options.options object is populated/updated as a side effect of calling parse_command_line and parse_config_file.

## Raises:
    IOError:
        - Raised by parse_config_file when the configuration file cannot be read.
        - The function catches IOError and suppresses it only if the basename of options.conf equals DEFAULT_CONFIG_FILE; otherwise it re-raises the IOError to signal an explicit/mistakenly-specified missing config file.
    Other exceptions:
        - Exceptions propagated directly from parse_command_line or from is_flower_option (e.g., AttributeError on non-string argv elements) are not caught here and will propagate to the caller.

## Constraints:
Preconditions:
    - prog_name should be a string and argv should be an iterable of strings representing CLI tokens.
    - The local helper is_flower_option is expected to be present in the same module (it is present in the provided snapshot). The function relies on is_flower_option to identify which argv tokens correspond to tornado.options.
    - tornado.options.options must be importable and have a conf attribute (options.conf) set to a path or filename.

Postconditions:
    - tornado.options.options will reflect values parsed from:
        1) CLI tokens (filtered to Flower options) parsed before reading config file,
        2) Values from the parsed config file (if successfully read), then
        3) CLI tokens re-applied so CLI flags override config values.
    - If a non-default config file was specified but could not be read, an IOError will be raised and the caller should treat initialization as failed; partial option state may already have been applied.

## Side Effects:
    - I/O: Attempts to open and read the file at os.path.abspath(options.conf) via parse_config_file.
    - Mutates global state: updates the global tornado.options.options object by calling parse_command_line and parse_config_file.
    - No direct network I/O or stdout/stderr printing performed by this function itself (but tornado parsing functions may log).
    - Potential to raise exceptions that propagate to process startup and may terminate initialization.

## Control Flow:
flowchart TD
    A[Start: receive prog_name, argv] --> B[Filter argv with is_flower_option]
    B --> C[Call parse_command_line([prog_name] + filtered_argv)]
    C --> D{Attempt parse_config_file(os.path.abspath(options.conf))}
    D -- Success --> E[Call parse_command_line([prog_name] + filtered_argv) again]
    E --> F[Return None (options updated)]
    D -- IOError --> G{basename(options.conf) == DEFAULT_CONFIG_FILE ?}
    G -- Yes --> H[Suppress IOError -> Return None (options updated from CLI only)]
    G -- No --> I[Re-raise IOError -> propagate failure]

## Examples:
    Example 1 — Typical startup usage:
        # Called early during process start with program name and argv tokens.
        apply_options('flower', sys.argv[1:])
        # After this call, tornado.options.options holds the parsed configuration.

    Example 2 — Behavior when config file is missing:
        # If options.conf is set to the bundle default name (DEFAULT_CONFIG_FILE)
        # and that file is absent, apply_options will ignore the missing file and continue.
        # If options.conf points to a custom file path that does not exist,
        # apply_options will raise the IOError from parse_config_file.

    Example 3 — Error handling by caller:
        try:
            apply_options('flower', cli_args)
        except IOError as exc:
            # A custom config file was requested but could not be read; abort startup.
            logging.error('Unable to read config file: %s', exc)
            raise

## `flower.command.warn_about_celery_args_used_in_flower_command` · *function*

## Summary:
Checks a list of Flower command-line arguments and logs a warning if any of them are actually Celery options that were mistakenly placed after the "flower" subcommand.

## Description:
- Known callers within the current snapshot: No direct callers were found in the provided repository slice. Intended use: this function is designed to be invoked during CLI argument handling for the Celery/Flower command-line interface, typically as part of the Flower subcommand argument processing when a click Context (ctx) is available.
- Typical trigger: run after parsing the Flower subcommand arguments to detect user mistakes where Celery-level options were specified after the "flower" command rather than before it.
- Responsibility boundary: encapsulates only the detection and logging of incorrectly placed Celery options. It does not modify arguments, raise errors, or perform any command dispatch; it only inspects the Click context and the provided flower_args and emits a warning when misplacement is detected. This extraction keeps the CLI parsing and warning logic separate so callers can decide whether to continue, abort, or adjust behavior.

## Args:
    ctx (click.Context):
        - A Click Context object for the current command invocation.
        - Preconditions: ctx.parent must exist and ctx.parent.command must be an object exposing a .params iterable. Each element of .params must expose an .opts iterable (list/tuple) of option strings (e.g., ['--broker', '-b']).
        - Typical origin: passed by Click when used as a callback or called explicitly during command handling.
    flower_args (Iterable[str]):
        - An iterable (typically list) of argument strings that were provided after the "flower" subcommand.
        - Each element is expected to be a string; elements may be plain option names (e.g., --port) or key=value style (e.g., --broker=amqp://...).
        - The function splits each value on the first '=' and uses the left-hand side (the option name) for matching.

## Returns:
    None
    - The function always returns None (no explicit return). Its observable effect is logging a warning when misused options are discovered.

## Raises:
    - AttributeError:
        - If ctx, ctx.parent, ctx.parent.command, or any expected attributes (.params, .opts) are missing, attribute access will raise AttributeError.
    - TypeError:
        - If elements of flower_args are not strings, str.partition may raise TypeError (or the membership check semantics will behave unexpectedly).
    - Note: the function does not intentionally raise exceptions; the above are incidental from incorrect argument shapes or a malformed Click context.

## Constraints:
- Preconditions:
    - ctx must be a Click Context with a valid parent command that exposes .params and each param has .opts.
    - flower_args must be an iterable of strings.
- Postconditions:
    - No mutation of inputs occurs.
    - If any incorrectly placed Celery arguments were found, a warning log has been emitted containing the list of offending option names; otherwise no logging occurs and nothing is changed.

## Side Effects:
- Emits a warning via the module-level logger (logger.warning). This is the only side effect.
- No file, network, stdout writes (beyond logger handlers), database or global state mutations are performed by this function itself.
- The exact destination of the warning depends on the logging configuration of the host application.

## Control Flow:
flowchart TD
    Start([Start])
    BuildOptions[/"Collect celery_options from ctx.parent.command.params -> param.opts"/]
    IterateArgs["For each arg in flower_args\n- split at first '=' -> arg_name\n- check if arg_name in celery_options"]
    AddIfMatch{"arg_name in celery_options?"}
    Append[/"append arg_name to incorrectly_used_args"/]
    AfterLoop["Finished iterating flower_args"]
    CheckList{"incorrectly_used_args not empty?"}
    LogWarning[/Log warning with incorrectly_used_args/]
    End([End])

    Start --> BuildOptions --> IterateArgs --> AddIfMatch
    AddIfMatch -- yes --> Append --> IterateArgs
    AddIfMatch -- no --> IterateArgs
    IterateArgs --> AfterLoop --> CheckList
    CheckList -- yes --> LogWarning --> End
    CheckList -- no --> End

## Examples:
- Incorrect CLI usage (triggers the warning):
    celery flower --broker=amqp://guest:guest@localhost:5672//
  Explanation: the option --broker is a Celery-level option and should appear before the "flower" subcommand; placing it after "flower" is what this function detects and warns about.

- Correct CLI usage (no warning):
    celery --broker=amqp://guest:guest@localhost:5672// flower --port=5555
  Explanation: Celery options appear before the "flower" subcommand and Flower-specific options appear after it; no warning will be logged.

- Calling from a Click-based handler (conceptual):
    - The caller supplies the Click ctx and a list of the arguments passed to the flower subcommand (flower_args). After calling this function, the caller can continue normal processing; the function only logs a warning if needed.

## Implementation Notes (for reimplementation):
- To reimplement:
    1. Build celery_options as a flattened list: for each param in ctx.parent.command.params, extend with param.opts (these are option strings).
    2. For each string in flower_args, isolate the option name by splitting on the first '=' (use str.partition or equivalent) and check membership in celery_options.
    3. Collect any matches into incorrectly_used_args.
    4. If the collection is non-empty, call logger.warning with a human-readable message and the list of offending names.
- Matching is an exact string comparison: the function does not normalize option names, strip whitespace, or perform prefix matching. Ensure callers supply option names in the same form used in param.opts (e.g., '--broker').

## `flower.command.setup_logging` · *function*

## Summary:
Sets up Tornado-related logging behavior for the Flower process: switches to pretty debug logging when debug mode is enabled and otherwise silences Tornado access logs by attaching a NullHandler and disabling propagation.

## Description:
This function centralizes the logic used to configure logging related to Tornado access logs and pretty printing for debug mode.

Known callers within the provided repository snapshot:
    - None found in the scanned codebase. (The function is defined in flower.command and is intended to be invoked during application startup once options have been parsed.)

Typical trigger/context:
    - Call after application options have been parsed (for example, after parse_command_line or parse_config_file) and before starting the web server or main event loop. It enforces a consistent logging configuration based on the parsed runtime options.

Why this logic is extracted:
    - Separates logging setup concerns from command-line parsing and application startup code.
    - Encapsulates the policy: when debug mode is requested, enable pretty logging; otherwise, prevent Tornado access logs from cluttering output by silencing them.
    - Keeps the codebase DRY and makes the logging behavior easy to locate and modify.

## Args:
    - None

## Returns:
    - None
    - The function performs configuration side effects and does not return a value.

## Raises:
    - AttributeError: If the global options object does not have the attributes `debug` or `logging` accessed by the function, attribute access will raise AttributeError.
    - Any exceptions raised by enable_pretty_logging() (tornado.log.enable_pretty_logging) will propagate unchanged.

## Constraints:
Preconditions:
    - The global `options` (from tornado.options) must be imported and populated. The function expects `options.debug` and `options.logging` attributes to exist.
    - The module imports must have been successful: enable_pretty_logging (from tornado.log) and NullHandler (from logging) must be available.

Postconditions:
    - If options.debug is truthy and options.logging equals the string 'info':
        - options.logging will be set to 'debug'
        - enable_pretty_logging() will have been called (which configures Tornado's logging to a development-friendly format).
    - Otherwise:
        - A NullHandler instance will have been added to the "tornado.access" logger.
        - The "tornado.access" logger's propagate flag will have been set to False, preventing propagation to ancestor loggers.

## Side Effects:
    - Mutates global state: updates `options.logging` when switching to debug.
    - Modifies the Python logging system:
        - Calls enable_pretty_logging() in the debug path (which configures tornado logging handlers and format).
        - Adds a NullHandler to the "tornado.access" logger in the non-debug path.
        - Sets logging.getLogger("tornado.access").propagate = False in the non-debug path.
    - No file or network I/O is performed by this function itself (aside from effects caused by enable_pretty_logging()).
    - No return value; behavior is entirely via side effects.

## Control Flow:
flowchart TD
    Start --> CheckOptions
    CheckOptions -->|options.debug is truthy AND options.logging == 'info'| DebugPath
    CheckOptions -->|otherwise| NonDebugPath
    DebugPath --> SetOptionsLoggingDebug
    SetOptionsLoggingDebug --> CallEnablePrettyLogging
    CallEnablePrettyLogging --> End
    NonDebugPath --> GetTornadoAccessLogger
    GetTornadoAccessLogger --> AddNullHandler
    AddNullHandler --> SetPropagateFalse
    SetPropagateFalse --> End

## Examples:
Example 1 — Typical startup sequence (happy path):
    1. parse_command_line() or parse_config_file() populate `options`.
    2. Call setup_logging() to apply logging policy based on parsed options.
    3. Start web server / main loop.

    # Pseudocode (non-executable illustrative sequence)
    parse_command_line()
    setup_logging()
    start_flower_application()

Example 2 — Safe invocation with defensive handling:
    # If you cannot guarantee that options has required attributes, guard against AttributeError
    try:
        setup_logging()
    except AttributeError:
        # fallback: configure a minimal logging policy or re-raise with context
        logging.getLogger("tornado.access").addHandler(NullHandler())
        logging.getLogger("tornado.access").propagate = False

Notes:
    - The function relies on tornado.log.enable_pretty_logging to perform the debug-mode logging configuration. If Tornado's API changes, this function's behavior may need to be updated.
    - It intentionally silences Tornado access logs when not in debug/info mode to reduce noisy output; adjust if you require access logs in production.

## `flower.command.extract_settings` · *function*

## Summary:
Populate and normalize the global web application settings dict from parsed command-line/config options, applying URL prefixing, OAuth and SSL configuration, and validating authentication options.

## Description:
This function reads runtime configuration values from the Tornado/CLI `options` object and updates the shared `settings` mapping (imported from urls.settings) to reflect those runtime choices.

Known callers and typical context:
- Intended to be called during application startup/configuration prior to creating or starting the Flower web application (for example, after parsing command-line arguments / a config file and before instantiating the web app). Typical call site is early in the main command flow that boots the Flower process.
- The function centralizes the mapping of CLI/config options -> runtime settings consumed by web handlers and template logic.

Why this logic is extracted:
- It encapsulates the translation from CLI/config options to the web app's runtime settings in one place, keeping startup code simpler and making the mapping reusable and testable.
- It enforces a clear responsibility boundary: mutating the `settings` dict and validating auth-related options, while delegating path normalization and validation to small helper utilities (abs_path, prepend_url, validate_auth_option).

## Args:
This function takes no parameters; it reads values from external modules:
- Uses `options` (tornado.options options namespace) for all inputs:
    - options.debug (bool-like)
    - options.cookie_secret (str or falsy)
    - options.url_prefix (str or falsy)
    - options.auth (str or falsy)
    - options.oauth2_key, options.oauth2_secret, options.oauth2_redirect_uri (str or falsy)
    - options.certfile, options.keyfile, options.ca_certs (str paths or falsy)
- Uses environment variables as fallbacks for OAuth:
    - FLOWER_OAUTH2_KEY, FLOWER_OAUTH2_SECRET, FLOWER_OAUTH2_REDIRECT_URI

Note: No parameters are passed; all values are read from module-level `options` and environment.

## Returns:
- None. The effect of the function is to mutate the imported `settings` dict in-place. No value is returned.

All possible post-call effects on `settings`:
- settings['debug'] is set to options.debug (boolean-like).
- If options.cookie_secret is truthy: settings['cookie_secret'] is set to options.cookie_secret.
- If options.url_prefix is truthy: the function replaces settings['login_url'] and settings['static_url_prefix'] with prepend_url(settings[name], options.url_prefix).
- If options.auth is truthy: settings['oauth'] is set to a dict with keys:
    - 'key' -> options.oauth2_key or os.environ.get('FLOWER_OAUTH2_KEY')
    - 'secret' -> options.oauth2_secret or os.environ.get('FLOWER_OAUTH2_SECRET')
    - 'redirect_uri' -> options.oauth2_redirect_uri or os.environ.get('FLOWER_OAUTH2_REDIRECT_URI')
- If both options.certfile and options.keyfile are truthy: settings['ssl_options'] is set to a dict:
    - certfile -> abs_path(options.certfile)
    - keyfile -> abs_path(options.keyfile)
    - optionally ca_certs -> abs_path(options.ca_certs) if options.ca_certs is truthy

Edge-case returns:
- No return values. On invalid authentication option (options.auth present but validate_auth_option returns False), the function logs an error and terminates the process via sys.exit(1).

## Raises:
- SystemExit: The function will call sys.exit(1) (raising SystemExit) when:
    - options.auth is truthy AND validate_auth_option(options.auth) returns False.
- KeyError (implicit): If options.url_prefix is truthy but the imported `settings` mapping does not contain 'login_url' or 'static_url_prefix', attempting settings[name] will raise KeyError. The function does not guard against missing keys.
- Other exceptions propagated from helper functions:
    - abs_path(...) may raise if path processing raises (propagated).
    - prepend_url(...) may raise if it expects certain input shapes (propagated).
    - validate_auth_option(...) may raise if its implementation raises.

## Constraints:
Preconditions (what must be true before calling):
- The Tornado `options` namespace must be parsed/populated (e.g., parse_command_line or parse_config_file called) so the option attributes referenced exist.
- The module-level `settings` (imported from urls.settings) must be a mutable mapping and should contain the keys 'login_url' and 'static_url_prefix' if options.url_prefix may be provided.
- Helper functions used (prepend_url, abs_path, validate_auth_option) must be importable and behave as expected.

Postconditions (guarantees after return, unless a SystemExit is raised):
- The `settings` dict will reflect CLI/config driven changes described in "Returns".
- If options.auth was provided and valid, settings['oauth'] will exist and contain OAuth entries (possibly None values if neither options nor env vars provide them).
- If options.certfile and options.keyfile were provided, settings['ssl_options'] will be present with absolute paths.

## Side Effects:
- Mutates the imported `settings` dictionary in-place.
- Reads environment variables: FLOWER_OAUTH2_KEY, FLOWER_OAUTH2_SECRET, FLOWER_OAUTH2_REDIRECT_URI.
- Calls helper utilities: prepend_url (to prefix URLs), abs_path (to create absolute file paths), validate_auth_option (to check the auth option).
- Logs an error via the module logger (logger.error) when auth validation fails.
- May terminate the process via sys.exit(1) on invalid auth option.
- No direct filesystem writes or network I/O are performed by this function itself (though abs_path may perform path normalization only). No stdout is written directly.

## Control Flow:
flowchart TD
    Start[Start] --> SetDebug[Set settings['debug'] = options.debug]
    SetDebug --> CookieSecretCheck{options.cookie_secret?}
    CookieSecretCheck -- yes --> SetCookieSecret[settings['cookie_secret'] = options.cookie_secret]
    CookieSecretCheck -- no --> URLPrefixCheck{options.url_prefix?}
    SetCookieSecret --> URLPrefixCheck
    URLPrefixCheck -- yes --> LoopURLs[For name in login_url, static_url_prefix: settings[name] = prepend_url(...)]
    LoopURLs --> OAuthCheck{options.auth?}
    URLPrefixCheck -- no --> OAuthCheck
    OAuthCheck -- yes --> SetOAuth[settings['oauth'] = {'key':..., 'secret':..., 'redirect_uri':...}]
    OAuthCheck -- no --> SSLCheck{options.certfile and options.keyfile?}
    SetOAuth --> SSLCheck
    SSLCheck -- yes --> SetSSL[settings['ssl_options'] = {'certfile':abs_path(...),'keyfile':abs_path(...)}]
    SetSSL --> CACertsCheck{options.ca_certs?}
    SSLCheck -- no --> AuthValidateCheck{options.auth and not validate_auth_option(options.auth)?}
    CACertsCheck -- yes --> AddCACerts[settings['ssl_options']['ca_certs']=abs_path(...)]
    CACertsCheck -- no --> AuthValidateCheck
    AddCACerts --> AuthValidateCheck
    AuthValidateCheck -- yes --> LogErrorAndExit[logger.error(...); sys.exit(1)]
    AuthValidateCheck -- no --> End[Return]
    LogErrorAndExit --> End

## Examples:
Example startup flow (illustrative, not runnable as-is):
- Typical usage:
    - parse_command_line() or parse_config_file(...) to populate `options`
    - call extract_settings() to apply configuration to the runtime settings mapping
    - create the Flower/Tornado application which reads from `settings`

Pseudocode:
    parse_command_line()
    parse_config_file(config_path)   # if used
    extract_settings()               # apply CLI/config to runtime settings
    app = Flower(settings)           # instantiate application that uses settings
    app.start()

Example showing OAuth fallback to environment and handling invalid auth:
    # assume options.auth is truthy (e.g., "google")
    # options.oauth2_key is empty, environment variable FLOWER_OAUTH2_KEY is used instead
    os.environ['FLOWER_OAUTH2_KEY'] = 'env-key'
    parse_command_line('--auth=google')
    extract_settings()
    # after extract_settings: settings['oauth']['key'] == 'env-key'

Error handling:
    # If options.auth is present but validate_auth_option returns False,
    # extract_settings will log an error and exit the process with code 1.
    # Caller should ensure options.auth is of expected format, or be prepared
    # for process termination.

## `flower.command.is_flower_option` · *function*

## Summary:
Return whether the given command-line-style token corresponds to a configured Tornado option name (an attribute on the imported options object).

## Description:
This function is a small helper used when processing command-line arguments or configuration tokens to determine if a token represents a recognized option name managed by tornado.options (the imported options object). It extracts the logical option name from common CLI syntaxes (leading dashes, optional "=value", and dashed names) and checks for the presence of that name as an attribute on options.

Known callers within the codebase:
- No direct callers were found inside this file snapshot. The intended usage is from CLI parsing or command setup code that must decide whether an arg should be treated as a Flower/Tornado option (handled by tornado.options) versus a different kind of argument. Typical call sites are command-line argument iterators or option-filtering utilities invoked during process startup.

Why this logic is extracted:
- It centralizes the exact normalization rules (strip leading hyphens, split off an attached value, convert dashes to underscores) so callers don't duplicate parsing logic and so the decision of whether an argument is a recognized option is consistent across the codebase.

## Args:
    arg (str): A single command-line token representing an option or other CLI argument.
        - Expected format examples: '--port=5555', '-b', 'broker=redis://localhost', 'url-prefix'
        - The function treats any leading '-' characters as optional and will remove all of them.
        - If arg contains an '=' the substring before the first '=' is taken as the name.
        - Any '-' characters in the extracted name are converted to '_' before lookup.
        - Interdependencies: The function relies on the imported options object (from tornado.options) to determine known options.

## Returns:
    bool: True if, after normalization, the extracted name is an attribute on the imported options object; False otherwise.
    - Possible return values:
        - True: options has an attribute matching the normalized name (e.g., normalized name 'broker' => options.broker exists).
        - False: options does not have such an attribute (including empty names).
    - Edge cases:
        - If arg is an empty string or resolves to an empty name after stripping, the function returns False (most likely, since options rarely has an empty-string attribute).
        - If arg is a name without leading hyphens (e.g., 'port=5555'), it is still processed and may return True if options has that name.

## Raises:
    AttributeError (or similar): If arg is not a string-like object with lstrip/partition/replace methods, a Python exception will be raised when attempting to call those methods (for example, if arg is None or a non-string object). The function does not perform type-checking and does not raise custom exceptions.

## Constraints:
    Preconditions:
        - The global imported options object (tornado.options.options) must be available and valid in the module namespace.
        - Callers should pass a string or string-like object representing a CLI token.
    Postconditions:
        - No mutation of input or global state occurs.
        - The function returns a boolean and has no side effects.

## Side Effects:
    - None. The function performs pure in-memory computation and attribute lookup; it does not perform I/O, network calls, logging, or mutation of globals.

## Control Flow:
flowchart TD
    A[Start: receive arg] --> B{arg is string-like}
    B -- No --> E[Exception raised when calling lstrip/partition/replace]
    B -- Yes --> C[Strip all leading '-' characters: arg.lstrip('-')]
    C --> D[Split on first '=' -> name_before_equal]
    D --> F[Replace '-' with '_' in name]
    F --> G{options has attribute 'name'?}
    G -- Yes --> H[Return True]
    G -- No --> I[Return False]

## Examples:
    Example 1 — Typical use in CLI parsing:
        # Given options includes attribute 'port'
        is_flower_option('--port=5555')  # returns True
        is_flower_option('-port')        # returns True
        is_flower_option('port')         # returns True

    Example 2 — Dashed option name normalization:
        # Given options includes attribute 'url_prefix' (note underscore)
        is_flower_option('--url-prefix=/flower')  # returns True (normalized to 'url_prefix')

    Example 3 — Non-option token:
        is_flower_option('some-unknown-token')  # returns False if options.some_unknown_token does not exist

    Example 4 — Error handling for wrong input type:
        try:
            is_flower_option(None)  # will raise AttributeError because None has no lstrip method
        except AttributeError:
            # handle invalid token type
            pass

## `flower.command.is_flower_envvar` · *function*

## Summary:
Return whether an environment variable name represents a Flower configuration option by checking a module-level prefix and membership of the remainder (case-normalized) in the known option keys.

## Description:
This small predicate centralizes the decision rule used when scanning environment variables for application configuration. It performs two checks in order:
1. The env var name starts with a configured prefix (ENV_VAR_PREFIX).
2. The substring after that prefix, converted to lower case, is present in the collection of known option names (default_options).

Known callers:
- No explicit callers were present in the provided source excerpt. Typical callers are configuration-loading code that iterates over os.environ and converts matching entries into application options before initializing the Flower app.

Why extracted:
- Keeps environment-to-option mapping logic in a single testable location.
- Callers only need to iterate environment names and call this predicate, avoiding duplication and ensuring consistent prefix and membership semantics.

## Args:
    name (str):
        Environment variable name to test.
        - Expected type: str (or an object that implements startswith(str) and supports slicing and lower()).
        - Allowed values: any string; empty string is allowed but will usually fail the prefix test unless ENV_VAR_PREFIX is empty.
        - Interdependencies:
            * ENV_VAR_PREFIX (module-level): must be a string prefix that environment variable names are expected to start with.
            * default_options (module-level): a collection (set, list, tuple, dict-like) whose membership test is used; typically contains valid option names in lower-case or mixed-case. Membership is checked against the lower-cased remainder.

## Returns:
    bool:
        True if and only if:
        - name.startswith(ENV_VAR_PREFIX) is True (prefix match), AND
        - name[len(ENV_VAR_PREFIX):].lower() is in default_options (membership of the case-normalized remainder).
        Otherwise, returns False.

        Edge-case behaviors:
        - If name equals ENV_VAR_PREFIX exactly, the remainder is the empty string ''. The function returns True only if '' is a member of default_options.
        - If name is shorter than ENV_VAR_PREFIX, startswith returns False and the function returns False; the slicing and membership check are not evaluated because Python's "and" short-circuits.
        - If ENV_VAR_PREFIX is the empty string '', the function reduces to testing name.lower() in default_options (every name "starts with" the empty prefix).
        - Membership respects the semantics of the default_options container (e.g., dict membership checks keys).

## Raises:
    AttributeError or TypeError:
        If name is not string-like (e.g., None or an unrelated object) and does not implement startswith or lower, calling those methods will raise AttributeError or TypeError at runtime.

    NameError:
        If ENV_VAR_PREFIX or default_options are not defined in the module at runtime, attempting to evaluate them will raise NameError before this function runs.

## Constraints:
    Preconditions:
        - ENV_VAR_PREFIX must be defined and is expected to be a str.
        - default_options must be defined and support membership testing for strings (e.g., set, list, dict keys).
        - Caller should provide a str-like name.

    Postconditions:
        - The function has no side effects and does not change module state.
        - It deterministically returns a boolean based only on its inputs and the two module-level symbols.

## Side Effects:
    - None. Pure computation: no I/O, no mutation of globals, no network/database activity.

## Control Flow:
flowchart TD
    Start --> CheckPrefix
    CheckPrefix{"name.startswith(ENV_VAR_PREFIX) ?"}
    CheckPrefix -- False --> ReturnFalse1["return False (short-circuit; no slicing)"]
    CheckPrefix -- True --> SliceRest["rest = name[len(ENV_VAR_PREFIX):].lower()"]
    SliceRest --> CheckMembership{"rest in default_options ?"}
    CheckMembership -- True --> ReturnTrue["return True"]
    CheckMembership -- False --> ReturnFalse2["return False"]

## Examples:
Assume various hypothetical module configurations for illustration.

1) Standard prefix, known options:
    - ENV_VAR_PREFIX = 'FLOWER_'
    - default_options contains {'port', 'broker'}

    is_flower_envvar('FLOWER_PORT')      -> True   (remainder 'port' -> 'port' in default_options)
    is_flower_envvar('FLOWER_UNKNOWN')   -> False  (remainder 'unknown' not in default_options)
    is_flower_envvar('OTHER_FLOWER_PORT')-> False  (does not start with prefix)

2) Name equals prefix:
    - ENV_VAR_PREFIX = 'FLOWER_'
    - default_options does NOT contain ''
    is_flower_envvar('FLOWER_') -> False

    If default_options contains '' then the result would be True (rare and not recommended).

3) Name shorter than prefix:
    - ENV_VAR_PREFIX = 'FLOWER_LONG_'
    is_flower_envvar('SHORT') -> False (startswith fails; slicing not evaluated)

4) Empty prefix:
    - ENV_VAR_PREFIX = ''
    - default_options contains {'debug'}
    is_flower_envvar('DEBUG') -> True  ('' prefix always matches; remainder 'DEBUG'.lower() == 'debug')

Usage pattern (pseudo):
    for key in os.environ:
        if is_flower_envvar(key):
            opt_name = key[len(ENV_VAR_PREFIX):].lower()
            # apply os.environ[key] to application configuration under opt_name

## `flower.command.print_banner` · *function*

## Summary:
Logs startup information to the module logger: the access URL (HTTP/HTTPS) or unix-socket path, the broker URI, a sorted, pretty-printed list of registered task names, and a debug dump of settings.

## Description:
- Known callers:
    - No explicit call sites were included in the provided context. Typically this function is invoked once at server startup after:
        1. command-line/config options have been parsed (tornado.options.options),
        2. a Flower or Celery application instance (app) has been created and initialized.
      Typical caller locations are the CLI or startup routines that boot the Flower web UI.
- Responsibility boundary:
    - This function centralizes informational startup logging. It does not perform initialization, network binding, or configuration—only reads configuration and application state and emits log messages. Keeping this in a single function avoids duplicating startup logging across multiple entrypoints.

## Args:
    app (object):
        - Required.
        - Expected interface:
            * app.connection() -> connection object with as_uri() method that returns a broker URI string.
            * app.tasks -> mapping-like object (e.g., dict) whose keys() are the registered task names (expected to be strings).
        - Behavior on invalid app:
            * If app lacks .connection or .tasks, AttributeError will be raised by this function.
            * If app.connection().as_uri() raises, that exception will propagate.
            * If app.tasks.keys() yields elements that cannot be compared during sorting (e.g., mixed incomparable types), sorted(...) will raise TypeError.
    ssl (bool):
        - Required.
        - Interpreted by truthiness: if truthy, the protocol printed becomes "https" (via inserting 's'); otherwise "http".
        - No default; caller must supply.

## Returns:
    None
    - The function only emits log messages via the module-level logger and does not return a value.

## Raises:
    - AttributeError: if the provided app does not implement .connection() or .tasks as expected.
    - Any exception raised by app.connection() or by connection.as_uri() (e.g., runtime/broker errors) will propagate.
    - TypeError: if sorting app.tasks.keys() fails because keys are not mutually comparable.
    - Any exceptions raised while reading tornado.options.options attributes (unlikely if options are properly initialized) will propagate.
    - The function contains no explicit raise statements; all raised exceptions originate from called attribute access or built-in operations.

## Constraints:
- Preconditions (caller must ensure):
    - tornado.options.options has been parsed/initialized so that these attributes exist and reflect the desired configuration:
        * options.unix_socket
        * options.url_prefix
        * options.address
        * options.port
    - A module-level logger variable named logger exists and is configured (handlers/levels) by the application environment.
    - The app argument must be initialized and able to provide a connection and a tasks mapping.
- Postconditions:
    - After successful return, informational and debug log records have been emitted describing access instructions, broker URI, registered tasks list, and current settings snapshot.
    - No application state is mutated by this function itself (aside from any side effects of app.connection()).

## Side Effects:
- Logging:
    - Emits logger.info with:
        * Access message: either "Visit me at http[s]://<address>:<port><prefix_str>" or "Visit me via unix socket file: <unix_socket>"
        * Broker: 'Broker: <broker_uri>' (using app.connection().as_uri())
        * Registered tasks: 'Registered tasks: \n<pretty-printed sorted list>'
    - Emits logger.debug with a pformatted snapshot of settings (imported as settings).
    - The destination and appearance of these messages depend on global logger configuration (handlers, formatters, levels).
- No file, database, network writes are performed by this function itself. However, app.connection() may perform operations whose side effects are outside the scope of this function.

## Implementation details visible from code (important behaviors)
- URL formation:
    - If options.unix_socket is falsy:
        * prefix_str is set to f'/{options.url_prefix}/' when options.url_prefix is truthy; otherwise prefix_str is set to '' (empty string).
        * The protocol string is built by inserting 's' when ssl is truthy: "http" + ('s' if ssl else '') -> "https" when ssl True, "http" when ssl False.
        * The address displayed is options.address or the literal string '0.0.0.0' when options.address is falsy.
        * The function uses options.port directly (no conversion), so if port is None or a non-stringable type, the log formatting will represent it as Python's string conversion of that object (which may be "None").
    - If options.unix_socket is truthy:
        * The function logs the unix socket path from options.unix_socket instead of an HTTP URL.
- Tasks listing:
    - The function calls sorted(app.tasks.keys()) then pformat(...) to produce a human-readable, sorted list of task names. If task keys are not strings or not mutually comparable, sorted() may raise TypeError.
- Logging levels:
    - Access message: logger.info
    - Broker URI: logger.info
    - Registered tasks: logger.info
    - Settings: logger.debug

## Control Flow:
flowchart TD
    Start --> IsUnixSocket{options.unix_socket truthy?}
    IsUnixSocket -- No --> HasPrefix{options.url_prefix truthy?}
    HasPrefix -- Yes --> PrefixSet["prefix_str = '/' + options.url_prefix + '/'"]
    HasPrefix -- No --> PrefixSet["prefix_str = ''"]
    PrefixSet --> BuildProtocol["protocol = 'http' + ('s' if ssl else '')"]
    BuildProtocol --> BuildAddress["address = options.address or '0.0.0.0'"]
    BuildAddress --> LogHTTP["logger.info Visit me at <protocol>://<address>:<port><prefix_str>"]
    IsUnixSocket -- Yes --> LogSocket["logger.info Visit me via unix socket file: <options.unix_socket>"]
    LogHTTP --> LogBroker["logger.info Broker: <app.connection().as_uri()>"]
    LogSocket --> LogBroker
    LogBroker --> LogTasks["logger.info Registered tasks: <pformat(sorted(app.tasks.keys()))>"]
    LogTasks --> LogSettings["logger.debug Settings: <pformat(settings)>"]
    LogSettings --> End

## Examples:
- Example 1 — typical HTTP server startup (conceptual):
    - Precondition: options.unix_socket is falsy, options.url_prefix == 'flower', options.address is falsy, options.port == 5555, ssl == True.
    - Invocation: print_banner(app, ssl=True)
    - Effective logged lines (logger output; exact formatting depends on logger configuration):
        INFO  Visit me at https://0.0.0.0:5555/flower/
        INFO  Broker: amqp://guest:guest@localhost:5672//
        INFO  Registered tasks:
        INFO  ['task.add', 'task.mul', 'task.user.process']
        DEBUG Settings: {'some_setting': 'value', ...}
- Example 2 — unix socket mode:
    - Precondition: options.unix_socket == '/var/run/flower.sock'
    - Invocation: print_banner(app, ssl=False)
    - Effect:
        INFO  Visit me via unix socket file: /var/run/flower.sock
        INFO  Broker: redis://localhost:6379/0
        INFO  Registered tasks:
        INFO  ['task.a', 'task.b']
        DEBUG Settings: {...}
- Error handling guidance:
    - If callers want to present a friendly error when the broker connection cannot be described, wrap the call:
        try:
            print_banner(app, ssl)
        except Exception as exc:
            logger.error("Failed to print startup banner: %s", exc)
            # handle fallback behavior (continue without broker info, retry, or exit)

