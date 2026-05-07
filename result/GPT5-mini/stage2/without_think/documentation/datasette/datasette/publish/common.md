# `common.py`

## `datasette.publish.common.add_common_publish_arguments_and_options` · *function*

## Summary:
Attach a standard set of Click arguments and options commonly used by datasette "publish" subcommands to a Click subcommand function, returning the callable augmented with Click metadata.

## Description:
This helper applies a fixed list of Click argument/option decorators to the provided subcommand callable so all publish-related CLI commands share a consistent set of flags and parsing behavior.

Known callers and invocation context:
- Intended to be used by publish-related CLI command definitions to add a common surface of options. In typical usage it is applied to a Click subcommand function at definition time (either by wrapping the function or placing the helper above the command function as a decorator).
- No direct call-site file names were discovered in the available scan; treat Click-based publish subcommands as the runtime callers (Click invokes the decorated function when the command runs and Click itself handles parsing of the options added here).

Why this is extracted:
- Centralizes and standardizes CLI options/options parsing for all publish commands so that each subcommand need not duplicate the long list of flags.
- Keeps option declarations and option-specific parsing/validation consistent and easy to maintain (for example, wiring of validate_plugin_secret and StaticMount occurs in one place).

## Args:
    subcommand (callable)
        The Click subcommand function to which the common decorators will be applied.
        - Expected to be a callable compatible with Click (a function that will receive keyword arguments produced by Click option parsing).
        - The helper accepts any callable; however, callers should ensure the callable is meant to be a Click command (so Click will later call it with parameters produced by the options added here).

## Returns:
    callable
        The same callable passed in, decorated with multiple Click argument and option decorators.
        - The returned callable is modified so Click will parse and pass the following arguments/options when the command is invoked:
            * files: variadic file paths (click.Path, must exist)
            * metadata: opened file (click.File, read mode) or None
            * extra-options: string
            * branch: string
            * template-dir: existing directory path (click.Path, dir_okay True)
            * plugins-dir: existing directory path (click.Path, dir_okay True)
            * static: one or more mount specifications parsed by StaticMount (see Side Effects)
            * install: one or more strings (packages to install)
            * plugin-secret: zero or more 3-tuples (plugin, setting, value) validated by validate_plugin_secret
            * version-note: string
            * secret: string; default is supplied as a callable that produces a 32-byte random hex string if environment variable DATASETTE_PUBLISH_SECRET is not set
            * title, license, license_url, source, source_url, about, about_url: strings for metadata
        - The exact types and parsing behaviors are determined by Click types passed to click.argument/option in the helper (see Side Effects and Description for details).

## Raises:
    None (the helper itself performs no runtime validation that raises exceptions).
    - Note: some of the Click parameter types and callbacks wired here will raise when Click parses user input at CLI runtime:
        * validate_plugin_secret (used as callback for --plugin-secret) will raise click.BadParameter if any secret contains a single quote.
        * StaticMount (used as the type for --static) will call its convert method and call fail on invalid format or non-existent/non-directory paths, causing Click to report an error.
        * click.Path and click.File types will cause Click to raise if provided paths do not meet their constraints (for example non-existent files when exists=True).

## Constraints:
Preconditions:
    - The provided subcommand must be a callable intended to be used as a Click command; it should accept the keyword arguments that Click will supply for the added options.
    - The Click library must be used as the CLI framework at runtime (this helper wires Click decorators).

Postconditions:
    - The returned callable has Click decoration metadata attached (parameters list, option parsing configuration).
    - When Click invokes the decorated callable during command execution, Click will supply the parsed option/argument values as keyword arguments according to the types and multiplicity specified here.

## Side Effects:
    - No filesystem, network, or external I/O is performed by this helper at decoration time.
    - Mutation of the provided callable: applying Click decorators attaches metadata (parameters and option configuration) to the callable and returns that modified callable. That metadata is used later by Click during argument parsing.
    - Runtime side effects occur later when Click parses user input:
        * click.File(type=click.File(mode="r")) will open the metadata file for reading and pass a file-like object to the command function (or raise if the file cannot be opened).
        * StaticMount type will validate and return a tuple (mount_point, absolute_directory_path); it fails if the input doesn't contain ":" or the directory does not exist or is not a directory.
        * validate_plugin_secret callback will validate each 3-tuple supplied to --plugin-secret and raise click.BadParameter if any secret contains a single quote.
        * The secret option has envvar DATASETTE_PUBLISH_SECRET; if not set, Click will use the provided default callable to supply a random hex secret at runtime.

## Control Flow:
flowchart TD
    Start --> BuildDecorators[Create tuple of Click decorators]
    BuildDecorators --> Reverse[Reverse the decorators sequence]
    Reverse --> ForLoop[For each decorator in reversed tuple]
    ForLoop --> Apply{Apply decorator to subcommand}
    Apply --> NextIter[Set subcommand = decorator(subcommand)]
    NextIter --> ForLoop
    ForLoop --> Done[All decorators applied]
    Done --> Return[Return decorated subcommand]
    Return --> End

## Examples:
Usage pattern (described in prose):
- Apply this helper to a Click subcommand so the subcommand gains all publish-related options. This can be done by wrapping the subcommand callable with this helper at definition time or by using it as a decorator above the subcommand function. After decoration, when the command is invoked by Click, the command function will receive parsed values for the options listed above as keyword arguments.

How to interpret some option values inside the command body:
- files: a sequence (tuple) of filesystem paths as strings; each path is validated to exist by click.Path.
- metadata: either a file-like object opened for reading (if provided) or None; callers should read and parse JSON/YAML from this file-like object when present.
- --static entries: each provided value is converted by StaticMount into a tuple (mount_point, absolute_directory_path). mount_point is the path at which files will be served, and absolute_directory_path is the validated directory path on disk.
- --plugin-secret entries: Click will present these as an iterable of 3-tuples (plugin_name, plugin_setting, setting_value). The validate_plugin_secret callback rejects any setting_value that contains a single quote; otherwise these tuples are passed through unchanged.
- secret: a string used for signing; if the environment variable DATASETTE_PUBLISH_SECRET is not set, Click will obtain a default by invoking the callable that produces a 32-byte random hex string.

Error handling notes:
- Validation errors originating from option types or callbacks are surfaced to the end user by Click with appropriate error messages; the command body will not execute if parsing/validation fails.
- Commands should defensively handle optional values (for example, metadata may be absent) and treat multiple-valued options as sequences.

## `datasette.publish.common.fail_if_publish_binary_not_installed` · *function*

## Summary:
Checks whether a required external CLI binary is available on PATH and, if it is missing, prints a clear error and installation hint to stderr and terminates the process with exit code 1.

## Description:
This small helper is intended to be used by publish target implementations or CLI command handlers immediately before attempting any operation that relies on an external command-line tool. Typical usage is inside a publish command or target-specific deployment flow to fail fast with a helpful message when the external tool is not installed or not discoverable in PATH.

Known callers in the provided context:
- No explicit callers were included in the preloaded source for this task. In the Datasette codebase this function is intended to be called by publish-subcommand handlers and modules that implement publishing to remote targets (for example, code paths that prepare and invoke Heroku, Fly, or other provider CLIs) prior to invoking the external binary.

Why this logic is extracted:
- Centralizes the responsibility for checking availability of required external binaries, so all publish targets produce a consistent, user-friendly error message and exit behavior.
- Keeps publish target implementations focused on orchestration and leaves detection and messaging policy in one place.

## Args:
    binary (str): The executable name to look for (e.g., "heroku", "fly", "gcloud"). This is passed directly to shutil.which; expected to be a non-empty string.
    publish_target (str): Human-readable name of the publish target (e.g., "Heroku"). Used only to produce contextual error text.
    install_link (str): URL or textual instruction pointing the user to installation instructions. Displayed verbatim in the follow-up message.

Interdependencies:
- All three arguments are used only for user-facing messages and the binary name for lookup. There is no validation beyond passing them into shutil.which and formatting strings.

## Returns:
    None

Behavior detail:
- If the binary is found (shutil.which(binary) returns a non-empty path), the function returns normally (None) and execution continues.
- If the binary is not found (shutil.which(binary) returns None or falsy), the function does not return; it writes two messages to stderr and terminates the process with exit code 1 by calling sys.exit(1).

## Raises:
    SystemExit: Raised via sys.exit(1) when the specified binary is not found on PATH. The exit code is exactly 1.

Note: the function does not raise other exceptions itself; any exceptions from shutil.which or click.* calls (unlikely under normal conditions) will propagate.

## Constraints:
Preconditions:
- Caller should provide string values for binary, publish_target, and install_link. The function assumes binary is a name suitable for shutil.which (i.e., a command name or path fragment).
- The environment's PATH and shutil.which behavior determine discoverability. On some platforms or environments, executables may not be discoverable if PATH is altered.

Postconditions:
- On normal return: shutil.which(binary) evaluated truthily (i.e., an executable path exists), and no I/O or process termination has occurred.
- On failure: process terminates with exit code 1; the error messages have been emitted to stderr.

## Side Effects:
- Writes a highlighted error line to stderr using click.secho with bg="red", fg="white", bold=True and err=True. The message has the form:
  "Publishing to {publish_target} requires {binary} to be installed and configured"
- Writes a second line to stderr using click.echo with err=True showing:
  "Follow the instructions at {install_link}"
- Calls sys.exit(1), which raises SystemExit and terminates the process with exit code 1 unless caught by the caller.

No file, network, or persistent state is modified by this function.

## Control Flow:
flowchart TD
    A[Start] --> B{shutil.which(binary) returns truthy?}
    B -- Yes --> C[Return None, continue execution]
    B -- No --> D[click.secho error to stderr]
    D --> E[click.echo install_link to stderr]
    E --> F[sys.exit(1) -> process exits with code 1]

## Examples:
- Typical in-CLI usage (described):
  1. Inside a publish command handler, before invoking the external tool, call this helper with the tool name, target label, and an installation URL.
  2. If the tool is present, the handler proceeds to run deployment steps.
  3. If the tool is missing, the helper prints a red, bold error message plus the installation link to stderr and exits the process with status 1.

- Unit test guidance:
  To assert the failure behavior in a test, call the function with a likely-nonexistent binary name (for determinism) and catch SystemExit. Then assert that the caught SystemExit has code 1 and that the captured stderr contains the expected phrases "requires {binary}" and the provided install_link. This lets tests verify both the exit code and the user-facing messages without allowing the test runner process to terminate.

## `datasette.publish.common.validate_plugin_secret` · *function*

## Summary:
Checks each plugin-secret triplet and rejects the input if any secret contains a single quote, otherwise returns the original iterable unchanged.

## Description:
A Click-style option callback that validates values supplied to a CLI option (commonly --plugin-secret) during option parsing. It inspects the third element (secret value) of each entry provided and enforces a single rule: secret values must not contain the single quote character (').

Known callers and invocation context:
- Intended to be used as the callback for a Click option on publish-related CLI commands; Click calls this function with the signature (ctx, param, value) during option parsing.
- No direct call-sites were discovered in the provided file scan; treat Click itself (via the option machinery) as the runtime caller when the option is present.
- Typical trigger: user passes one or more --plugin-secret entries on the command line; Click assembles those entries into an iterable and invokes this callback before the command body runs.

Why this is a separate function:
- Encapsulates input validation and user-facing error messaging for plugin secrets in a single, reusable place.
- Keeps CLI option declarations concise and centralizes a policy (no single quotes in secrets) so changes affect all callers uniformly.

## Args:
    ctx (click.Context)
        The Click invocation context. Required by Click's callback signature but not used by this function.
    param (click.Parameter)
        The Click parameter definition object. Required by Click's callback signature but not used by this function.
    value (iterable[tuple[str, str, str]])
        An iterable (for example, list or tuple) of 3-tuples. Each tuple must contain:
            - plugin_name (str): plugin identifier (not inspected)
            - plugin_setting (str): setting name (not inspected)
            - setting_value (str): secret value to validate (inspected)
        The function unpacks each element with "for plugin_name, plugin_setting, setting_value in value:", so each element must be an iterable of exactly three items. setting_value is expected to be a str; non-str values may cause a TypeError when checking membership.

## Returns:
    The same value object passed in (iterable[tuple[str, str, str]]), unmodified.
    - If no secret contains a single quote, the original iterable is returned to allow Click to continue processing.
    - If value is an empty iterable, it is returned unchanged.

## Raises:
    click.BadParameter
        Raised when any setting_value contains a single quote character (').
        - Exact message: "--plugin-secret cannot contain single quotes"
    ValueError (propagated)
        May be raised by Python during tuple unpacking if an element of value does not have exactly three items (e.g., "not enough values to unpack" or "too many values to unpack").
    TypeError (propagated)
        May be raised if value is not iterable, or if a non-string setting_value does not support the membership test "'" in setting_value.

## Constraints:
Preconditions:
    - Caller must pass an iterable of 3-item iterables (triplets). Each triplet's third element should be a string.
    - The function follows the Click callback protocol (accepts ctx and param), so it should be registered as a Click callback.

Postconditions:
    - If the function returns normally, every inspected setting_value contained no single-quote characters.
    - The input iterable is not modified by this function.

## Side Effects:
    - None. This function does not perform I/O, logging, network access, or mutate global state. It only raises exceptions to indicate invalid input.

## Control Flow:
flowchart TD
    Start --> ForEach[For each (plugin_name, plugin_setting, setting_value) in value]
    ForEach --> Check{"Does setting_value contain the single quote (')?"}
    Check -- Yes --> RaiseBad[Raise click.BadParameter with message]
    Check -- No --> Next[Proceed to next tuple]
    Next --> ForEach
    ForEach --> End[Return original value]

## Examples:
- Valid input (returns input):
    value = [("myplugin", "secret_key", "abc123"), ("p2", "key", "long-secret-456")]
    Call result: returns the same list unchanged.

- Invalid input (raises click.BadParameter):
    value = [("myplugin", "secret_key", "pass'word")]
    Call result: raises click.BadParameter("--plugin-secret cannot contain single quotes")

- Malformed entry (propagates unpacking error):
    value = [("only_two_items", "missing_secret")]
    Call result: Python raises ValueError during unpacking (not caught by this function).

- Typical Click wiring (conceptual):
    The option that collects plugin-secret entries uses this function as its callback. During parsing, Click passes (ctx, param, value) to the function; if a click.BadParameter is raised, Click reports the error to the user and aborts command execution.

