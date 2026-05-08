# `main.py`

## `mackup.main.ColorFormatCodes` · *class*

## Summary:
A static namespace providing three ANSI terminal escape-code strings for blue text, bold text, and resetting terminal formatting.

## Description:
ColorFormatCodes is a lightweight container class that groups three ANSI escape-sequence constants used to format terminal output. It does not implement behavior, hold runtime state, or require instantiation; callers access its attributes directly via the class name (for example, ColorFormatCodes.BLUE).

Intended use:
- Embed the constants before text to apply formatting and append NORMAL afterwards to reset formatting.
- Useful for CLI output formatting in environments that support ANSI escape codes.

Notes about callers:
- The source file does not specify which modules use these constants. Any code that prints to a terminal and wants simple inline formatting may import and reference these attributes.

Environment constraints:
- These escape codes are effective only on terminals that interpret ANSI sequences. On terminals without ANSI support the raw escape sequences will be printed.

## State:
- Attributes (class-level constants; no instance attributes):
  - BLUE (str)
    - Value: "\033[34m"
    - Purpose: switch subsequent text color to blue.
  - BOLD (str)
    - Value: "\033[1m"
    - Purpose: apply bold/intensified weight to subsequent text (visual effect depends on terminal).
  - NORMAL (str)
    - Value: "\033[0m"
    - Purpose: reset all terminal attributes (color, weight, etc.) to defaults.

Type and mutability:
- All attributes are plain Python strings. The class does not enforce immutability; they can be rebound at runtime by any code that has access to the class object. Such mutation would affect any future use of these attributes across the process.

Class-level invariant (intended):
- Formatted output should be followed by NORMAL to avoid leaking formatting. This is a usage convention; it is not enforced by the class.

## Lifecycle:
- Creation:
  - No constructor arguments. Instantiation is unnecessary. If instantiated, the instance carries no additional state or behavior.
- Usage:
  - Access constants via the class: ColorFormatCodes.BLUE, ColorFormatCodes.BOLD, ColorFormatCodes.NORMAL.
  - Typical pattern: prefix formatting constants, emit content, then emit NORMAL.
  - There is no required call order enforced by the class.
- Destruction:
  - No cleanup or resource management is provided or required.

## Method Map:
Note: The class has no methods. The following diagram shows the typical formatting usage flow.

graph TD
    A[Select formatting constant (BLUE/BOLD)] --> B[Construct output string: prefix + content]
    B --> C[Emit output]
    C --> D[Emit NORMAL to reset formatting]
    D --> E[Continue with unformatted output]

## Raises:
- The class definition and attribute access do not raise exceptions.
- Any exceptions that occur while using these constants arise from the caller's code (for example, TypeError when concatenating non-strings), not from this class.

## Example:
- Print blue text and reset:
print(ColorFormatCodes.BLUE + "Status: OK" + ColorFormatCodes.NORMAL)

- Print bold blue text and reset:
print(ColorFormatCodes.BOLD + ColorFormatCodes.BLUE + "Important message" + ColorFormatCodes.NORMAL)

## `mackup.main.header` · *function*

## Summary:
Return the input text wrapped with ANSI escape sequences that set the terminal color to blue and then reset formatting, producing a single formatted string for CLI output.

## Description:
- Known callers: No direct callers were visible in the provided snapshot. This function is part of the CLI module and intended for use by printing routines that render program headers, section titles, or other emphasized lines in terminal output.
- Responsibility boundary: Encapsulates the exact formatting pattern (BLUE prefix and NORMAL suffix) so callers do not duplicate ANSI escape sequences. It isolates terminal-formatting concerns from presentation logic.

## Args:
    str (str): Text to be formatted.
        - Required positional parameter; the function uses this identifier exactly as declared in the source.
        - Must be a Python str instance in common usage. If a non-str is supplied and cannot participate in string concatenation with str, a TypeError is raised.
        - Note: the parameter name shadows the built-in type name 'str' in the local scope. Callers should avoid relying on the built-in within the same scope.

## Returns:
    str: A new Python string equal to ColorFormatCodes.BLUE + str + ColorFormatCodes.NORMAL, assuming ColorFormatCodes and its attributes exist and are strings.
        - Example result (typical): "\033[34mHello\033[0m"
        - Edge cases:
            - If input is the empty string, the return value will still contain the prefix and suffix escape codes (e.g., "\033[34m\033[0m").
            - If ColorFormatCodes.BLUE or ColorFormatCodes.NORMAL are empty strings, the return value will effectively be the original input or partially wrapped accordingly.

## Raises:
    NameError: If the name ColorFormatCodes is not defined in the runtime scope when the function is executed.
        - Trigger: Reference to an undefined global name.
    AttributeError: If ColorFormatCodes exists but lacks the BLUE or NORMAL attributes.
        - Trigger: Attempting to access ColorFormatCodes.BLUE or ColorFormatCodes.NORMAL when not present.
    TypeError: If the provided argument cannot be concatenated with the surrounding ANSI strings.
        - Typical trigger: argument is not a str and neither side’s __add__/__radd__ implementations return a str.
        - Note: In rare cases an object's __radd__ may allow successful concatenation; callers should not rely on that behavior and should convert non-str inputs explicitly with str().

## Constraints:
- Preconditions:
    - ColorFormatCodes must be defined and accessible in the function's global scope.
    - ColorFormatCodes.BLUE and ColorFormatCodes.NORMAL must be strings (ANSI escape sequences) for the function to produce the intended formatted output without raising TypeError.
- Postconditions:
    - If the call returns normally, the returned string begins with the BLUE sequence and ends with the NORMAL sequence (subject to the attributes being strings).
    - No global state or external resources are modified by this function.

## Side Effects:
- The function itself has no I/O, no printing, and no external side effects — it only constructs and returns a string.
- When the returned string is printed to a terminal, visible formatting occurs only on terminals that interpret ANSI escape sequences. On terminals without ANSI support, the raw escape sequences will appear.

## Control Flow:
flowchart TD
    Start --> CheckColorDef{Is ColorFormatCodes defined?}
    CheckColorDef -->|No| RaiseNameError[Raise NameError]
    CheckColorDef -->|Yes| CheckAttrs{Has BLUE and NORMAL attributes?}
    CheckAttrs -->|No| RaiseAttributeError[Raise AttributeError]
    CheckAttrs -->|Yes| CheckInput{Is input a str instance?}
    CheckInput -->|Yes| BuildReturn[Return BLUE + input + NORMAL]
    CheckInput -->|No| TryConcat[Attempt concatenation]
    TryConcat -->|Succeeds (object provides __radd__ returning str)| BuildReturn
    TryConcat -->|Fails| RaiseTypeError[TypeError raised by Python]

## Examples:
- Typical usage:
print(header("Mackup — Configuration Backup"))

- Converting non-str values to avoid TypeError:
value = 123
print(header(str(value)))  # safe: explicitly convert to string before formatting

- Defensive wrapper ensuring no exceptions escape:
def safe_header_print(x):
    try:
        print(header(x))
    except (NameError, AttributeError):
        # Formatting subsystem missing; fall back to plain text
        print(str(x))
    except TypeError:
        # Convert to string fallback
        print(str(x))

## `mackup.main.bold` · *function*

## Summary:
Wraps the given text with ANSI escape sequences that enable bold formatting in ANSI-capable terminals and then resets terminal formatting.

## Description:
- Known callers: No direct call sites for this function were identified in the provided repository snapshot. Typically this function is used by CLI presentation code to emphasize short pieces of terminal output immediately before printing (for example, when building messages printed to stdout).
- Responsibility boundary: This function performs a single, small formatting transformation — it composes the BOLD and NORMAL ANSI escape-code constants around a provided string. It intentionally does not perform type coercion, printing, or terminal capability detection; those responsibilities belong to caller code (output routines or CLI logic). Extracting this composition into its own function centralizes the exact sequence of escape codes so formatting usage is consistent and easy to update.

## Args:
    str (str): The input text to format. Must be a native Python string (type exactly str or a subclass). The function performs string concatenation and does not coerce non-string inputs; passing a non-str will raise a TypeError from Python's concatenation semantics.
    - No default value.
    - Note: the parameter name intentionally shadows the built-in type name 'str' because the function's implementation uses that identifier; callers should pass a string value despite the name.

## Returns:
    str: A new string equal to ColorFormatCodes.BOLD + str + ColorFormatCodes.NORMAL.
    - Represents the original content with a leading ANSI "bold" code and a trailing ANSI "reset" code.
    - If the input is the empty string, the return is the BOLD code immediately followed by the NORMAL code (i.e., formatting with no visible content in between).

## Raises:
    TypeError: If the provided argument is not a string (for example, an int, list, or object without a string type), Python's '+' string-concatenation operator will raise a TypeError. This is the only exception directly provoked by the function as implemented.
    - If ColorFormatCodes attributes have been mutated to non-string values, concatenation may raise TypeError as well.

## Constraints:
- Preconditions:
    - ColorFormatCodes.BOLD and ColorFormatCodes.NORMAL must be defined and be strings (the code assumes these class attributes exist).
    - Caller must provide a str instance as the argument.
- Postconditions:
    - The function returns a string that begins with ColorFormatCodes.BOLD and ends with ColorFormatCodes.NORMAL.
    - The function does not emit output or change global state.

## Side Effects:
- None intrinsic to this function: it performs no I/O, does not mutate global state, and makes no external service calls.
- Indirect effect: when the returned string is printed to an ANSI-capable terminal, the terminal will render the enclosed text in bold until the trailing reset code is processed.

## Control Flow:
flowchart TD
    Start([Start]) --> ReceiveArg{Receive argument 'str'}
    ReceiveArg --> IsString?{Is argument a str instance at runtime?}
    IsString? -- Yes --> Concat[Return ColorFormatCodes.BOLD + str + ColorFormatCodes.NORMAL]
    IsString? -- No --> RuntimeError[Python raises TypeError during concatenation]
    Concat --> End([End])
    RuntimeError --> End

## Examples:
- Typical usage (happy path):
print(bold("Warning: configuration missing"))  # prints "Warning: configuration missing" in bold on ANSI terminals

- Handling incorrect input gracefully:
try:
    print(bold(42))  # incorrect: 42 is not a str
except TypeError:
    print("Formatting failed: input must be a string")

- Empty-string case:
print(bold(""))  # prints only the bold start and reset sequences; no visible characters between them

## `mackup.main.main` · *function*

## Summary:
Parse CLI arguments and orchestrate the chosen Mackup command (backup, restore, uninstall, list, or show), delegating all filesystem work to Mackup and ApplicationProfile helpers and performing final temporary-folder cleanup.

## Description:
- Known callers:
    - Intended as the CLI entrypoint. Typical invocation paths are:
        * Executing the package as a script (console entry point or if __name__ == "__main__": main()).
        * A wrapper script or console_scripts entry that calls this function when the user runs the mackup command.
    - There are no other internal call sites in the provided repository snapshot; it is the top-level orchestration function for user-driven operations.
- Typical trigger:
    - User runs the command-line tool with arguments (for example: mackup backup --verbose). The function parses CLI options via docopt and runs the corresponding workflow.
- Responsibility boundary:
    - This function is purely an orchestration layer: parse options, set a few global flags in utils, instantiate core controller objects (Mackup, ApplicationsDatabase), and dispatch to per-operation logic (creating ApplicationProfile instances and calling backup/restore/uninstall). It intentionally does not implement low-level filesystem logic — those are delegated to Mackup and ApplicationProfile methods — and it ensures a single final cleanup call (mckp.clean_temp_folder()).

## Args:
- None (no function parameters).
- Implicit input:
    - Command-line arguments parsed from __doc__ by docopt.
    - Environment variables and system state used indirectly by instantiated components (for example, HOME, the file system, and process UID).

## Returns:
- None.
- The function either returns normally (None) after completing the chosen operation and running cleanup, or it terminates the process by raising SystemExit (see Raises).

## Raises:
- SystemExit:
    - Raised by docopt when the provided CLI arguments are invalid or when the user requests version/help output (docopt may call sys.exit internally).
    - Explicitly raised in the "show" branch when an unsupported application name is requested:
        * Condition: args["show"] is True and args["<application>"] not in app_db.get_app_names()
        * Effect: sys.exit("Unsupported application: {}".format(app_name))
    - Raised indirectly by Mackup environment checks:
        * Mackup.check_for_usable_environment() and Mackup.check_for_usable_restore_env() call utils.error(...) which calls sys.exit. Conditions include running as root when utils.CAN_RUN_AS_ROOT is False, or missing configured storage folder.
    - Raised indirectly by other helpers that call sys.exit or utils.error when they detect fatal preconditions.
- Exceptions propagated from components:
    - ApplicationsDatabase() constructor:
        * May raise KeyError if HOME is missing, ValueError for malformed cfg entries, configparser.NoSectionError/NoOptionError if a required [application] "name" is missing, or OSError/FileNotFoundError for filesystem access problems.
    - ApplicationProfile methods (backup, restore, uninstall):
        * May raise ValueError for unsupported file types, OSError/PermissionError/FileNotFoundError for filesystem operations (copy/delete/link), or AssertionError from utility functions if internal assertions fail.
    - Any of the above exceptions propagate out of main unless handled by higher-level code or cause process termination via SystemExit.

## Constraints:
- Preconditions:
    - The module-level __doc__ must contain a docopt-compatible usage string so docopt(__doc__) can parse arguments correctly.
    - Environment variables required by downstream components must be present and correct (notably HOME, and any environment assumed by ApplicationsDatabase and ApplicationProfile).
    - The utils module must expose mutable global flags FORCE_YES and CAN_RUN_AS_ROOT (main assigns to them).
    - The local variable verbose is referenced by the nested printAppHeader closure; verbose must be set (it is assigned before printAppHeader is ever invoked in the function's control flow).
    - The process should run on a platform that supports calls invoked by underlying components (for example os.geteuid used by Mackup.check_for_usable_environment on POSIX).
- Postconditions:
    - On normal completion (no fatal exception): temporary workspace created by Mackup during this run has been removed via mckp.clean_temp_folder().
    - The chosen per-application actions (backup/restore/uninstall) have been attempted by delegating to ApplicationProfile instances; their side-effects depend on those methods and on user confirmation when required.

## Side Effects:
- I/O and filesystem:
    - Delegated to ApplicationProfile.backup/restore/uninstall and Mackup methods:
        * May create, copy, delete, and symlink files and directories in the user's HOME and in the Mackup storage location.
        * ApplicationsDatabase() reads .cfg files from the bundled and custom apps directories during construction.
        * mckp.clean_temp_folder() removes the temporary directory created by the Mackup instance (destructive rmtree).
- Process / global state:
    - Mutates globals in utils:
        * If args["--force"] is True, sets utils.FORCE_YES = True (affects utils.confirm behavior).
        * If args["--root"] is True, sets utils.CAN_RUN_AS_ROOT = True (affects environment checks).
- Console I/O and user interaction:
    - Prints to stdout in multiple branches (application headers, supported-apps listing, verbose messages).
    - May prompt the user via utils.confirm(...) during uninstall/restore/backup flows (blocking stdin) unless FORCE_YES is set.
- Exit behavior:
    - May terminate the process via SystemExit raised by docopt, sys.exit(...) calls, or utils.error.

## Control Flow:
flowchart TD
    Start([Start]) --> ParseArgs[Parse CLI args via docopt(__doc__)]
    ParseArgs --> InitObjects[Instantiate Mackup() and ApplicationsDatabase()]
    InitObjects --> SetFlags{--force or --root present?}
    SetFlags --> AssignFlags[Set utils.FORCE_YES or utils.CAN_RUN_AS_ROOT as needed]
    AssignFlags --> AssignFlagsDone[Set dry_run and verbose]
    AssignFlagsDone --> Branch{Which action?}
    Branch -->|backup| BackupBranch
    Branch -->|restore| RestoreBranch
    Branch -->|uninstall| UninstallBranch
    Branch -->|list| ListBranch
    Branch -->|show| ShowBranch
    Branch -->|none/missing| EndNoop
    BackupBranch --> CheckBackupEnv[Mackup.check_for_usable_backup_env()]
    CheckBackupEnv --> ForEachBackup[For each app in mckp.get_apps_to_backup()]
    ForEachBackup --> CreateProfileBackup[ApplicationProfile(...); print header]
    CreateProfileBackup --> CallBackup[ApplicationProfile.backup()]
    CallBackup --> AfterAction
    RestoreBranch --> CheckRestoreEnv[Mackup.check_for_usable_restore_env()]
    CheckRestoreEnv --> RestoreMackupApp[restore Mackup app first]
    RestoreMackupApp --> Reinit[Mackup() and ApplicationsDatabase() re-created]
    Reinit --> ForEachRestore[For each remaining app in get_apps_to_backup()]
    ForEachRestore --> CreateProfileRestore[ApplicationProfile(...); print header]
    CreateProfileRestore --> CallRestore[ApplicationProfile.restore()]
    CallRestore --> AfterAction
    UninstallBranch --> CheckRestoreEnv2[Mackup.check_for_usable_restore_env()]
    CheckRestoreEnv2 --> ConfirmUninstall{dry_run or user confirms?}
    ConfirmUninstall -->|No| SkipUninstall
    ConfirmUninstall -->|Yes| ForEachUninstall[iterate apps]
    ForEachUninstall --> CreateProfileUninstall[ApplicationProfile(...); print header]
    CreateProfileUninstall --> CallUninstall[ApplicationProfile.uninstall()]
    CallUninstall --> UninstallMackupApp[uninstall Mackup app]
    UninstallMackupApp --> PrintThanks[Print completion message]
    ListBranch --> CheckEnvList[Mackup.check_for_usable_environment()]
    CheckEnvList --> PrintList[Print supported apps and count]
    ShowBranch --> CheckEnvShow[Mackup.check_for_usable_environment()]
    CheckEnvShow --> ValidateApp{app in app_db.get_app_names()?}
    ValidateApp -->|No| ExitUnsupported[sys.exit("Unsupported application: ...")]
    ValidateApp -->|Yes| PrintShow[Print app name and config files]
    AfterAction --> Cleanup[mckp.clean_temp_folder()]
    SkipUninstall --> Cleanup
    EndNoop --> Cleanup
    Cleanup --> End([End])

## Examples:
- Typical CLI usage (shell):
    - Backup all supported applications, verbose:
        mackup backup --verbose
    - Restore everything from storage:
        mackup restore
    - List supported applications:
        mackup list
    - Show files for a specific application:
        mackup show vim
    - Uninstall Mackup (will prompt; use --force to skip confirmation):
        mackup uninstall
- Embedding the CLI in a wrapper:
    - When calling main() programmatically, be prepared to handle SystemExit and propagate or capture it:
        * If embedding, catch SystemExit to avoid stopping the host process and to read the exit message/code.
- Notes on error handling:
    - If ApplicationsDatabase construction fails (missing HOME, malformed .cfg), main will abort and propagate the exception (or the process may terminate with an error). Wrap the call in a try/except around main() if you need custom error handling in embedding contexts.

