# `interact.py`

## `imapclient.interact.command_line` · *function*

## Summary:
Parse command-line options for the interactive IMAP tool, merge them with package defaults or a configuration file, prompt interactively for any missing required credentials, and return a consolidated argparse.Namespace describing runtime configuration.

## Description:
This function centralizes CLI parsing and default-merging for the interactive IMAP tooling. It:
- Parses argv into known options (host, username, password, port, ssl/insecure, file).
- If a config file is requested (-f/--file), it delegates to parse_config_file() and returns that Namespace.
- Otherwise, it computes the final ssl boolean from the --insecure flag, retrieves package defaults from get_config_defaults(), fills in any missing configuration attributes from those defaults, and interactively prompts for missing compulsory values (host, username, password) using getpass().

Known callers within the repository snapshot:
- None in the provided snapshot. Typical callers are top-level CLI entry points or an interactive main() that then calls create_client_from_config() with the returned Namespace.

Why this logic is extracted:
- Provides a single, testable place for CLI parsing, validation, prompting, and default merging. Downstream code receives a ready-to-use Namespace and does not need to handle argv parsing, prompting, or environment/default merging itself.

## Args:
- This function takes no Python arguments; it reads command-line arguments from the process argv via argparse.parse_args().

Parsed CLI options (become attributes on the returned Namespace):
- host (Optional[str])
  - Flags: -H, --host
  - IMAP server hostname. If not provided (and not supplied by defaults), user is prompted.
- username (Optional[str])
  - Flags: -u, --username
  - Login username. If None after merging with defaults, user is prompted via getpass(). Note: an explicitly provided empty string remains an empty string (not treated as None).
- password (Optional[str])
  - Flags: -p, --password
  - Login password. If None after merging with defaults, user is prompted via getpass(). An explicitly provided empty string remains an empty string.
- port (Optional[int])
  - Flags: -P, --port
  - Parsed as int by argparse. Default is None; callers typically interpret None as "use 993 for TLS, 143 otherwise".
- ssl (Optional[bool])
  - Flags: -s, --ssl (store_true)
  - The ArgumentParser adds this with default None. If not using a config file, the function sets args.ssl = not args.insecure (so it becomes a bool).
- insecure (bool)
  - Flag: --insecure (store_true, default False)
  - If True, the function computes args.ssl = False.
- file (Optional[str])
  - Flags: -f, --file
  - If supplied, the function calls parse_config_file(file) and returns that Namespace directly.

Interdependencies and precedence:
- If -f/--file is supplied, command_line() checks whether any of these attributes evaluate truthy: host, username, password, port, ssl, insecure. If any of those are truthy the function calls parser.error(...) which prints an error and causes SystemExit. Important nuance: the check uses truthiness, not "was this option present on the command line" — e.g., an explicitly provided empty string for username ("--username ''") is falsy and will not trigger the parser.error check.
- When not using a config file, args.ssl is computed after parsing as args.ssl = not args.insecure, ensuring ssl is a bool.
- After computing ssl, the function iterates over get_config_defaults().items() and for each name:
  - Retrieves value = getattr(args, name, default_value)
  - If name is one of the compulsory_args ("host","username","password") and value is None, it prompts value = getpass(name + ": ")
  - It then sets setattr(args, name, value)
  - For non-compulsory names, the attribute is set to either the existing parsed value or the default_value.

## Returns:
argparse.Namespace
- When -f/--file is provided and passes the mutual-exclusion truthiness check, returns the Namespace produced by parse_config_file(file). That Namespace includes DEFAULT-section fields (host, port, ssl, username, password, oauth2 fields, expect_failure, etc.) and an attribute alternates (dict[str, argparse.Namespace]) for named profiles.
- When not using -f, returns the argparse.Namespace produced by argparse with the following guarantees:
  - Attributes for all keys returned by get_config_defaults() are present on the Namespace after the merge loop (their values come from CLI, or defaults, or interactive prompt when compulsory and originally None).
  - host, username, and password will be non-None after the function returns (they will have been prompted if they remained None after merging).
  - args.ssl will be a boolean (True/False) because it is explicitly set as not args.insecure in the non-file code path.
  - port is int or None; other fields follow types described in get_config_defaults() (strings or None for getenv-based values; booleans for boolean flags).
- Edge cases:
  - If -f is used and parse_config_file raises exceptions (ValueError or configparser-related errors), those exceptions propagate.
  - If parse_args() or parser.error() detect invalid CLI usage, argparse will print an error and raise SystemExit (terminating the process unless caught).
  - If getpass() cannot read input (no tty) it may raise EOFError; if the user interrupts, KeyboardInterrupt may be raised. These exceptions propagate.

## Raises:
- SystemExit
  - Raised by argparse.parse_args() on parse errors or by parser.error() when -f is given together with any of the checked truthy attributes (host, username, password, port, ssl, insecure). The effect is process termination unless SystemExit is caught by the caller.
- ValueError
  - Propagated when parse_config_file(file) raises ValueError (for example, when DEFAULT in the file sets expect_failure, as parse_config_file enforces).
- configparser.NoSectionError / configparser.NoOptionError
  - May propagate from parse_config_file() when required options are missing in the config file.
- EOFError, KeyboardInterrupt
  - May be raised by getpass() when prompting for host/username/password in non-interactive environments or on user interrupt; these are not caught inside command_line().

## Constraints:
Preconditions:
- Designed for CLI execution: sys.argv should contain desired arguments.
- For interactive prompting to succeed, stdin must be available (a tty); otherwise getpass() may raise EOFError.
- If -f is provided, the path should be readable; parse_config_file() will attempt to open/read it.

Postconditions:
- On successful return (non-file path):
  - The returned Namespace contains all keys from get_config_defaults() as attributes.
  - Compulsory attributes host, username, password are guaranteed to be non-None.
  - args.ssl is a bool value.
- On successful return (file path):
  - The returned Namespace is whatever parse_config_file() returns; it includes alternates and typed fields produced by _read_config_section.

## Side Effects:
- Reads process argv via argparse.parse_args().
- May perform file I/O indirectly via parse_config_file(file).
- Prompts to stderr and reads from stdin via getpass() for missing compulsory credentials.
- Calls get_config_defaults() which reads environment variables (imapclient_*); those reads have no side effects.
- Does not perform network I/O, database writes, or persistent global state modification.

## Control Flow:
flowchart TD
    Start --> ParseArgs[call argparse.parse_args()]
    ParseArgs --> IfFile{args.file provided?}
    IfFile -- Yes --> TruthyCheck{args.host or args.username or args.password or args.port or args.ssl or args.insecure (truthy)?}
    TruthyCheck -- Yes --> ParserError[parser.error(...) -> SystemExit]
    TruthyCheck -- No --> ParseConfig[args = parse_config_file(file) -> return args]
    IfFile -- No --> ComputeSSL[args.ssl := not args.insecure]
    ComputeSSL --> GetDefaults[defaults := get_config_defaults()]
    GetDefaults --> Loop[for each (name, default_value) in defaults.items()]
    Loop --> GetValue[value := getattr(args, name, default_value)]
    GetValue --> IsCompulsory{name in ("host","username","password")?}
    IsCompulsory -- Yes --> IsNone{value is None?}
    IsNone -- Yes --> Prompt[getpass(name + ": ") -> value]
    IsNone -- No --> SkipPrompt
    Prompt --> SetAttr[setattr(args, name, value)]
    SkipPrompt --> SetAttr
    SetAttr --> Loop
    Loop --> ReturnArgs[return args]
    ReturnArgs --> End

## Examples:
1) Non-file example (interactive prompt):
- Invocation: tool --insecure --port 143
- Behavior:
  - parse_args() produces args with insecure=True, port=143, other attributes None.
  - args.ssl is set to False (not args.insecure).
  - get_config_defaults() is merged in for missing keys.
  - If host, username, or password remain None after merging, getpass() prompts the user.
  - Returns a Namespace with ssl=False, port=143, and non-None host/username/password.

2) File example:
- Invocation: tool -f /etc/imapclient/config.ini
- Behavior:
  - If no other truthy options are present, command_line() returns parse_config_file("/etc/imapclient/config.ini")'s Namespace.
  - That Namespace contains DEFAULT fields (host, port, ssl, username, password, oauth2 fields, expect_failure, etc.) and alternates mapping of named profiles.

3) Error example:
- Invocation: tool -f conf.ini --username alice
- Behavior:
  - Because args.username is truthy, command_line() calls parser.error(...), argparse prints an error and raises SystemExit; the function does not return normally.

Notes:
- The mutual-exclusion check for -f uses truthiness of certain attributes. This is a behavioral detail of the current implementation: an explicitly supplied empty string for a field (""), which is falsy, will not trigger the mutual-exclusion parser.error check even though the user provided that option on the command line.
- Consumers of the returned Namespace should interpret None values (e.g., port=None) according to their own semantics (e.g., selecting default IMAP ports).

## `imapclient.interact.main` · *function*

## Summary:
Start an interactive IMAP shell: parse CLI options, create an IMAP client from those options, and drop into the first available interactive Python shell with the connected client bound as the variable "c". Returns an exit status integer (0 on normal completion).

## Description:
- Known callers within the provided snapshot:
  - None found. Typical usage is as a CLI entry point (console_script) or invoked as the main function of an interactive tool that wants to expose a live IMAPClient to a developer.
- What this function does and why it is extracted:
  - Responsibility: orchestrates command-line parsing, client construction, and selection of an interactive shell. It centralizes the lifecycle required to present a ready-to-use interactive environment (variable "c") to a developer, so callers need not handle parsing, connection setup, or shell selection.
  - It is separated from other logic because it coordinates multiple independent concerns (argument handling via command_line(), client creation via create_client_from_config(), and runtime shell dispatch). Keeping this orchestration in one small function simplifies testing and reuse of the individual pieces.

## Args:
- None. main reads process argv via command_line().

## Returns:
int
- 0: Normal completion. main always returns 0 at the end of its run path after a shell session is entered and the session exits normally.
- main does not return other integer values in the current implementation; errors are reported as exceptions (see Raises).

## Raises:
- SystemExit
  - When command_line() invokes argparse-related termination (parse errors or explicit parser.error()); this will terminate the process unless caught by the caller.
- EOFError, KeyboardInterrupt
  - May be raised by command_line() while prompting for credentials (getpass) and propagate out of main if not caught elsewhere.
- Any exception raised by create_client_from_config(args)
  - main calls create_client_from_config(args) and does not catch its exceptions; any error during client creation (network, authentication, configuration parsing inside that function) will propagate.
- Any exception raised by a shell callback other than ImportError
  - The loop only catches ImportError for each shell attempt. If a selected shell raises a different exception while starting or running, that exception will propagate and cause main to exit with an uncaught exception.
- Note: ImportError raised by attempting to import a particular shell implementation is swallowed for that attempt and the code tries the next shell.

## Constraints:
- Preconditions:
  - Designed to be run in a CLI process where command_line() can read sys.argv and (if needed) prompt the user. For interactive prompts to succeed, stdin should be a TTY; otherwise getpass() in command_line() may raise EOFError.
  - The environment must provide any configuration files referenced by command-line options (if -f/--file is used) and create_client_from_config should be callable with the Namespace returned by command_line().
- Postconditions:
  - If main returns 0, a shell session was entered and exited normally; during that session an IMAP client object was made available to the user under the name "c".
  - No global state is explicitly modified by main itself beyond printing to stdout; any state change is performed by create_client_from_config or by user actions executed within the interactive shell.

## Side Effects:
- Stdout: prints the fixed messages "Connecting..." and "Connected." to indicate progress.
- Network / I/O: may occur indirectly through create_client_from_config(args) (e.g., opening network sockets to an IMAP server) — main does not perform networking directly but immediately uses whatever side effects occur inside create_client_from_config.
- Interactive Shells:
  - The running interactive shell executes arbitrary user code; that code can perform arbitrary side effects (filesystem, network, process, etc.). The built-in interactive variant exposes the client as local name "c"; ptpython and IPython variants place the client into their interactive contexts as well (banner notes the variable name).
- Imports at runtime:
  - main performs late imports inside nested functions for interactive shells (ptpython, IPython variants) and the builtin code module. An ImportError for a shell import is handled by trying the next shell backend.

## Control Flow:
flowchart TD
    Start --> ParseArgs[call command_line()]
    ParseArgs --> PrintConnecting[print "Connecting..."]
    PrintConnecting --> CreateClient[client = create_client_from_config(args)]
    CreateClient --> PrintConnected[print "Connected."]
    PrintConnected --> PrepareBanner[banner := 'IMAPClient instance is "c"']
    PrepareBanner --> ShellAttempts[define shell callback functions and tuple]
    ShellAttempts --> ForLoop[for shell in shell_attempts]
    ForLoop --> TryShell[try shell(client)]
    TryShell --> ImportErr{ImportError raised?}
    ImportErr -- Yes --> ContinueLoop[next shell]
    ImportErr -- No --> SuccessBreak[break out of loop]
    SuccessBreak --> Return0[return 0]
    TryShell --> OtherException{other exception?}
    OtherException -- Yes --> Propagate[exception propagates out of main]
    Propagate --> End
    ContinueLoop --> ForLoop
    Return0 --> End

## Examples:
1) Typical CLI entry (non-file path):
- User runs the tool without a config file. The function:
  - calls command_line() which may prompt for missing host/username/password;
  - prints "Connecting..." then "Connected." when client creation returns;
  - drops into the first available shell (ptpython, IPython variants, or built-in interactive). Inside that shell the developer can access the IMAP client as variable c.

2) Typical CLI entry (file path):
- User runs the tool with -f path/to/config.ini. command_line() returns a Namespace built from the file (or raises SystemExit/config parsing errors). main uses that Namespace to construct the client and then proceeds to shell selection as above.

3) Error handling from the caller's perspective:
- If the user supplies invalid CLI flags, argparse (via command_line()) will call parser.error() and raise SystemExit; a wrapper that wants to display a custom message should catch SystemExit around main() invocation.
- If create_client_from_config fails (network/auth/config error), the exception will propagate and should be handled by the process-level CLI wrapper if a graceful message is desired.

Notes:
- The interactive environment always binds the IMAPClient instance under the variable name "c" (the banner explicitly documents this). The exact behavior of the client (methods available, whether the connection is live, etc.) depends on create_client_from_config.

