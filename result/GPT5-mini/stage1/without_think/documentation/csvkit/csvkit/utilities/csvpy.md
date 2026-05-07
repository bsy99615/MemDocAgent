# `csvpy.py`

## `csvkit.utilities.csvpy.CSVPy` · *class*

## Summary:
CSVPy is a CLI utility class that loads a CSV file into an in-memory reader/table object (agate.csv.reader, agate.csv.DictReader, or agate.Table) and then drops the user into an interactive Python shell with that object bound to a named variable.

## Description:
CSVPy is intended to be used as a command-line subcommand within the csvkit suite (it subclasses CSVKitUtility). It handles adding two command-line switches (--dict and --agate), choosing an appropriate agate-based reader or table constructor, creating the reader/table from a specified input file, and launching an interactive REPL with the loaded CSV object available to the user.

Typical scenarios:
- A developer or data analyst wants to quickly inspect or experiment with the rows of a CSV file interactively.
- Called by the csvkit CLI dispatch machinery (CSVKitUtility) when the user selects the csvpy command.

Motivation & responsibility boundary:
- Responsibility: convert a provided CSV input file into an easily accessible Python object and provide an interactive environment to inspect or manipulate it.
- Boundaries: CSVPy does not implement CSV parsing itself— it delegates to agate.csv.reader, agate.csv.DictReader, or agate.Table.from_csv. It also does not manage full CLI argument parsing lifecycle beyond registering its own flags; it relies on CSVKitUtility for wiring argparser, argument parsing, and for providing attributes like input_file, args, and reader_kwargs.

Known callers / instantiation:
- Normally instantiated and invoked by the csvkit CLI framework (CSVKitUtility runner). It is not typically created directly by end-users; however, it can be used programmatically if the caller sets the expected attributes described below before invoking main().

## State:
Public / relevant attributes (inherited or provided by the CSVKitUtility contract):

- description (str)
  - Value: 'Load a CSV file into a CSV reader and then drop into a Python shell.' (class attribute)
  - Invariant: constant descriptive string used for CLI help text.

- argparser (argparse.ArgumentParser)
  - Type: argparse.ArgumentParser
  - Usage: add_arguments registers two flags on this parser; CSVKitUtility is expected to provide a configured parser prior to calling add_arguments.
  - Constraint: must be present and mutable when add_arguments() is called.

- args (argparse.Namespace)
  - Type: argparse.Namespace
  - Contents (used by CSVPy):
      - as_dict (bool): True if the user supplied --dict
      - as_agate (bool): True if the user supplied --agate
  - Valid values: booleans; both False is permitted (default behavior uses agate.csv.reader).
  - Invariant: args reflects parsed command-line options at the time main() is invoked.

- input_file (file-like object)
  - Type: readable file-like object (text-mode), must have a .name attribute (str)
  - Expected operations: readable stream passed into agate reader/constructor
  - Constraint: CSVPy will reject stdio piped input (input_file must not be sys.stdin).
  - Invariant: input_file is open and readable when main() is called.

- reader_kwargs (dict)
  - Type: dict[str, object]
  - Semantics: keyword arguments forwarded to the chosen agate reader/constructor (klass(self.input_file, **self.reader_kwargs)).
  - Typical values: encoding, dialect, newline handling, or other agate-specific reader options determined by CSVKitUtility.
  - Constraint: must be a mapping; can be empty.

Transient local names inside main():
- klass (callable): one of agate.csv.reader, agate.csv.DictReader, or agate.Table.from_csv
- class_name (str): human-readable name of klass for welcome message
- variable_name (str): 'reader' or 'table' — the name bound inside the interactive shell
- variable (object): the result of klass(self.input_file, **self.reader_kwargs)

Class invariants:
- When main() finishes the selection stage, variable is always bound to the object returned from klass(*).
- If input_file refers to sys.stdin, main() will not proceed to load data (argparser.error is raised) — ensuring CSVPy never attempts to load piped STDIN.

## Lifecycle:
Creation:
- Typical creation is handled by csvkit's CLI framework which supplies:
  - an argparse.ArgumentParser instance assigned to self.argparser
  - parsed arguments assigned to self.args after add_arguments() and parsing
  - an open input_file assigned to self.input_file
  - a dictionary of reader_kwargs assigned to self.reader_kwargs
- To construct programmatically, a caller must:
  1) instantiate CSVPy()
  2) ensure self.argparser exists and call add_arguments() so flags are registered
  3) set self.args to a Namespace containing boolean attributes as_dict and as_agate (result of parsing)
  4) set self.input_file to an open, readable file-like object (must not be sys.stdin)
  5) set self.reader_kwargs to a suitable dict (or empty dict)
  6) call main()

Usage (method order & sequencing):
1) add_arguments()
   - Register supported CLI flags (--dict and --agate) on self.argparser. Must be called before parsing CLI args so their presence is recognized.
2) (CSVKitUtility or caller) parse arguments and set self.args
3) main()
   - Validates that input_file is not sys.stdin; otherwise raises parser error.
   - Reads the input_file.name for the welcome message.
   - Selects appropriate loader based on flags: --dict => agate.csv.DictReader; --agate => agate.Table.from_csv; default => agate.csv.reader.
   - Instantiates the loader with input_file and reader_kwargs.
   - Attempts to launch an IPython terminal (InteractiveShellEmbed); if IPython is unavailable, falls back to the standard library code.interact REPL.
   - In the launched REPL the loaded object will be available under the recommended name 'reader' or 'table'.

Destruction / cleanup:
- CSVPy does not implement explicit resource cleanup. The caller is responsible for opening and closing input_file if it was created programmatically.
- When used via the CLI framework, file closing and other lifecycle tasks are managed by the surrounding framework.
- No context-manager support is implemented by CSVPy itself.

## Method Map:
graph TD
    A[add_arguments()] --> B[argparser has --dict, --agate]
    B --> C[args parsed (as_dict/as_agate)]
    C --> D[main()]
    D --> E{input_file == sys.stdin?}
    E -- yes --> F[argparser.error(...) -> abort]
    E -- no --> G[choose klass]
    G --> H[klass = agate.csv.DictReader OR agate.Table.from_csv OR agate.csv.reader]
    H --> I[variable = klass(input_file, **reader_kwargs)]
    I --> J[compose welcome_message]
    J --> K{Try IPython}
    K -- success --> L[bind variable name via exec; start InteractiveShellEmbed(banner1=welcome_message)]
    K -- ImportError --> M[start code.interact(banner, local={variable_name: variable})]

Notes:
- The diagram shows the primary control flow and decision points: STDIN rejection, klass selection, and IPython fallback.

## Raises:
- argparser.error (typically raises SystemExit or calls parser-specific error handling)
  - Trigger: if self.input_file == sys.stdin. This prevents using piped STDIN as input.
- Exceptions raised by the agate reader/constructor (klass(...))
  - Trigger: malformed CSV, unreadable file, or invalid reader_kwargs; these exceptions originate from agate and are not caught by CSVPy.
- ImportError
  - Trigger: attempting to import IPython's InteractiveShellEmbed may raise ImportError; this is caught internally and handled by falling back to the standard code.interact REPL.
- exec() usage: while not explicitly raising here, binding the variable name via exec() could raise SyntaxError if variable_name contains invalid Python identifier characters. CSVPy chooses variable_name from the small set {'reader', 'table'}, so this should not occur in normal operation.

## Example (programmatic usage steps):
1. Create an instance of CSVPy (in CSVKit this is done by the CLI runner).
2. Ensure argparser exists on the instance and call add_arguments() so that --dict and --agate flags are registered.
3. Parse or set args: ensure args has boolean attributes as_dict and as_agate reflecting whether the user requested a dict reader or an agate table.
4. Provide input_file as an open, readable file-like object (text mode) that is not sys.stdin, and set reader_kwargs to a dict of reader options (or an empty dict).
5. Call main():
   - CSVPy will select the appropriate agate loader, instantiate it with input_file and reader_kwargs, then open an interactive shell.
   - If IPython (InteractiveShellEmbed) is available, it will be used; otherwise code.interact will be used.
6. After the REPL exits, close input_file if you opened it programmatically.

Notes on interactive binding:
- The loaded object will be available inside the REPL under the name 'reader' when using agate.csv.reader or agate.csv.DictReader, and under 'table' when using agate.Table.from_csv. The welcome banner includes the filename and the type of the bound object.

### `csvkit.utilities.csvpy.CSVPy.add_arguments` · *method*

## Summary:
Registers two command-line options on the instance argument parser that toggle how the CSV input will be loaded; this mutates the parser state so subsequent argument parsing will produce boolean flags on self.args.

## Description:
This method adds two options to self.argparser:
- --dict: when present, indicates the CSV should be loaded as a DictReader (dest: as_dict).
- --agate: when present, indicates the CSV should be loaded as an agate Table (dest: as_agate).

Known callers and lifecycle:
- Intended to be invoked during the CLI setup/initialization phase before command-line arguments are parsed. In the csvkit CLI pattern, subclass utilities (such as CSVPy) expose add_arguments so the shared CLI bootstrap (the CSVKitUtility base/CLI harness) can call it while constructing the argument parser for the utility.
- After these options are registered and the parser parses argv, the rest of CSVPy.main reads self.args.as_dict and self.args.as_agate to choose the loading behavior.

Why this is a separate method:
- Keeps argument registration modular and overridable by subclasses; the CLI bootstrap can discover and run a uniform add_arguments hook on each utility, separating parser construction from runtime logic (main).
- Encapsulates all option definitions in one place for readability and easier extension or testing.

## Args:
This method has no external parameters beyond self.

## Effects on command-line arguments (explicitly registered options):
- --dict
    - dest: as_dict
    - action: store_true
    - type: bool (set to True if provided on the command line; False otherwise)
    - help: "Load the CSV file into a DictReader."
    - default: False (implicit from argparse store_true behavior)
- --agate
    - dest: as_agate
    - action: store_true
    - type: bool (set to True if provided on the command line; False otherwise)
    - help: "Load the CSV file into an agate table."
    - default: False (implicit from argparse store_true behavior)

## Returns:
- None

## Raises:
- AttributeError: if self.argparser is missing or does not expose an add_argument method (attempting to call self.argparser.add_argument will raise).
- Any exception raised by the underlying argument-parsing library when adding arguments (for example, errors produced by argparse if an option conflicts with an existing definition). The method itself does not catch such exceptions.

## State Changes:
- Attributes READ:
    - self.argparser — accessed to call add_argument.
- Attributes WRITTEN:
    - None of the object's own attributes (no assignment to self.<attr>).
    - Mutations: the internal state of self.argparser is modified (two new option definitions are registered, which affects subsequent parse results available as self.args).

## Constraints:
- Preconditions:
    - self.argparser must be initialized and must provide an add_argument method compatible with the signature used here (i.e., typical argparse.ArgumentParser or a compatible wrapper).
    - This method should be called prior to argument parsing (before parser.parse_args or equivalent), otherwise the new options will not affect the parsed result.
- Postconditions:
    - After successful execution, the parser will accept the --dict and --agate options. When parsed, the resulting namespace will include boolean attributes as_dict and as_agate (False if the option was not provided, True if provided).
    - No attributes on self are assigned by this method.

## Side Effects:
- No I/O is performed.
- Mutates self.argparser (a side effect visible outside the method because the parser is typically shared by the CLI bootstrap).
- No external services are called.

### `csvkit.utilities.csvpy.CSVPy.main` · *method*

## Summary:
Starts an interactive Python REPL (IPython if available, otherwise the builtin console) with the CSV data from the configured input file loaded into an in-memory object and bound to a short, well-known variable name so the user can immediately inspect and manipulate the data.

## Description:
This method is the runtime entry point invoked by the csvpy CLI command during the execution phase after argument parsing and input-file setup. It performs these steps:
- Validates that the configured input is not piped via STDIN (csvpy requires a filename).
- Selects which agate-backed loader to use based on CLI flags (--dict or --agate).
- Instantiates the chosen loader with the already-open input file and any reader keyword arguments.
- Prepares a human-friendly banner that identifies the loaded filename, the class used, and the variable name that the user can interact with.
- Attempts to launch an IPython interactive shell (preferred). If IPython is not installed, falls back to Python's built-in code.interact console. In both cases the loaded object is made available to the interactive session under a short name ('table' or 'reader').

Why this is a separate method:
- Encapsulates CLI validation, loader selection, object construction, and REPL setup into a single, testable operation specific to the csvpy command. Separating this logic simplifies the CLI command implementation and makes it easy to override or extend in subclasses.

Known callers and invocation context:
- Called by the CSVKit CLI dispatch/run process when the user runs the csvpy command. It runs during the CLI runtime phase after add_arguments has been called and self.args/self.input_file have been populated.

## Args:
This is an instance method and takes no explicit parameters. It relies on the following initialized attributes on self:
- self.input_file (file-like): An open, readable file-like object with a .name attribute (string). It must not be equal to sys.stdin.
- self.argparser (argparse.ArgumentParser-like): Used for error reporting via self.argparser.error(message).
- self.args (Namespace-like): Parsed CLI flags used to decide loader behavior:
    - as_dict (bool): If True, use agate.csv.DictReader.
    - as_agate (bool): If True, use agate.Table.from_csv.
- self.reader_kwargs (dict): Keyword arguments forwarded to the selected agate loader.

Flag precedence:
- If both --dict and --agate are supplied, the method gives precedence to --dict because of the if / elif ordering (as_dict is checked first). Thus as_dict > as_agate > default behavior.

## Returns:
- None. The method launches an interactive session; control returns to the caller only after the user exits the REPL (or the process terminates via an error). No explicit value is returned.

## Raises:
- SystemExit (via argparse error): If self.input_file == sys.stdin, self.argparser.error(...) is called. argparse.ArgumentParser.error normally terminates the process by calling sys.exit, which raises SystemExit.
- Any exception raised while constructing the agate reader/table (klass(self.input_file, **self.reader_kwargs)) will propagate (e.g., file I/O errors, encoding/decoding exceptions, agate parsing errors).
- ImportError for IPython is caught internally and handled by falling back to code.interact; it is not propagated.
- Exceptions raised by exec(...) or by launching/running the interactive shell (rare) are not caught here and will propagate to the caller.

## State Changes:
Attributes READ:
- self.input_file (and its .name)
- self.argparser
- self.args (including self.args.as_dict and self.args.as_agate)
- self.reader_kwargs

Attributes WRITTEN:
- None on self. The method does not assign to any self.<attr> fields.

Other runtime state changes:
- Binds the in-memory loaded object into the interactive session's namespace under a short name:
    - 'table' when --agate is used
    - 'reader' when --dict is used or when neither flag is used
  For the IPython path, the method first executes a simple assignment (exec) to create the name, then starts IPython; for the fallback, code.interact is called with a local mapping that explicitly contains the name. In both cases the effect is that the named variable is available inside the launched REPL.

## Constraints:
Preconditions:
- self.input_file must be an open, readable file-like object with a .name attribute.
- self.input_file must not be sys.stdin; otherwise the method will call self.argparser.error and exit.
- self.argparser and self.args must be previously initialized (argument parsing stage).
- self.reader_kwargs must be an acceptable mapping for the chosen agate loader.

Postconditions:
- An agate-backed object (agate.Table via Table.from_csv, an agate.csv.reader, or an agate.csv.DictReader) has been constructed from the contents of the provided input_file.
- The constructed object is accessible to the interactive session under the variable name 'table' or 'reader' as described above.
- The file object's position will be advanced according to how the chosen agate loader consumes the stream.

Safety notes:
- The method uses exec to perform a simple assignment such as "reader = variable" or "table = variable". This is safe here because variable_name is controlled by the code and is always one of the identifiers 'reader' or 'table'. No untrusted input is interpolated into exec.
- Because the interactive session allows arbitrary code execution, starting it hands control to the user; any side effects from that session (file writes, network access, process state changes) are possible.

## Side Effects:
- Reads from and consumes the underlying self.input_file.
- Launches an interactive REPL (IPython preferred). This hands control to the user and allows arbitrary code execution that can mutate process state or external systems.
- Displays a banner/welcome message that names the loaded file, class, and variable.
- Does not modify self attributes, but does create bindings in the launched interactive session's namespace so the user can access the loaded object immediately.

## Example usage (behavioral):
- After running csvpy against myfile.csv with no flags:
    - The utility constructs an agate.csv.reader and launches an interactive shell. Inside the shell the user can access the data via the variable reader.
- If run with --agate:
    - An agate.Table is created and available as table in the interactive session.
- If run with --dict:
    - An agate.csv.DictReader is created and available as reader. (as_dict takes precedence over as_agate.)

## `csvkit.utilities.csvpy.launch_new_instance` · *function*

## Summary:
Constructs a CSVPy CLI utility instance and hands control to its run() lifecycle, acting as a minimal bootstrap entry point that starts the interactive CSV REPL behavior.

## Description:
- Known callers and typical context:
  - Intended to be used as a module-level entry point for process startup (for example as a console_scripts packaging entry point), for integration tests that run the utility in-process, or any external runner that wants to invoke the CSVPy command behavior programmatically.
  - Typical trigger: the packaging/runtime imports the module and calls this function with no arguments to begin the CSVPy execution flow (argument parsing, input opening, CSV loading, and interactive shell launch).
- Why this logic is extracted into its own function:
  - Provides a stable, importable, and testable entry point that hides the CSVPy class name and instantiation details from packaging and runner code.
  - Keeps bootstrapping separate from the CSVPy implementation so callers can start the CLI behavior with a single, consistent call.
  - Delegates all parsing, I/O, and interactive REPL behavior to CSVPy.run(), keeping this wrapper trivial and predictable.

## Args:
- None.

## Returns:
- None.
  - The function returns implicitly after CSVPy.run() completes normally.
  - If CSVPy.run() blocks (for example while an interactive REPL is active), this function will block until run() returns or raises.
  - If CSVPy.run() raises an exception (including SystemExit), that exception propagates and the function does not return normally.

## Raises:
- NameError
  - Condition: The CSVPy symbol is not defined or importable in the module namespace when attempting to instantiate it (CSVPy()).
- Any exception raised by CSVPy.__init__
  - Condition: the CSVPy constructor raises during instantiation (e.g., missing required dependencies or constructor-time validation); the exception propagates unchanged.
- Any exception raised by CSVPy.run()
  - Condition: runtime failures during CSVPy.run(). Examples (originating from CSVPy.run, not this wrapper) include:
    - argparser.error triggered when CSVPy detects an unsupported input condition (for example, using sys.stdin as input when that is disallowed) — this often results in SystemExit or parser-specific termination behavior.
    - Exceptions raised by agate when loading or parsing the CSV (e.g., malformed CSV, I/O errors).
    - Other runtime exceptions raised inside CSVPy.run().
  - Note: CSVPy.run() internally handles some cases (for example, falling back from IPython to code.interact on ImportError). Such internally handled exceptions typically do not propagate out of run().

## Constraints:
- Preconditions:
  - The CSVPy symbol must exist in the module namespace and be constructable.
  - Any runtime context required by CSVPy.run() (for example, expected sys.argv contents, the presence of an input file or other CLI-provided resources) should be prepared by the caller; this wrapper does not set up CLI arguments or input streams.
- Postconditions:
  - If the function returns normally, CSVPy.run() has completed its lifecycle and any side effects performed by it (loading CSV, opening/closing files, running an interactive shell, printing to stdout/stderr, mutating global agate config) have already occurred.
  - No value is returned to indicate success; callers must rely on absence of raised exceptions or other externally observable side effects.

## Side Effects:
- This wrapper itself performs no direct I/O or global mutations beyond instantiating an object and calling its method.
- All observable side effects are produced by CSVPy.run(), and may include:
  - Reading a CSV input file and constructing an in-memory reader or agate table.
  - Launching an interactive REPL (IPython InteractiveShellEmbed if available, otherwise code.interact). The process will block until the REPL exits.
  - Printing a welcome banner to stdout/stderr describing the loaded object and filename.
  - Potentially raising SystemExit (via parser error) or other exceptions that propagate to the caller.
  - Any I/O, file descriptor usage, or global configuration changes performed by CSVPy.run() (for example changes to agate configuration) will be visible to the caller.

## Control Flow:
flowchart TD
    A[Call launch_new_instance()] --> B[Instantiate CSVPy()]
    B --> C{CSVPy.__init__ succeeds?}
    C -- no --> D[Constructor exception propagates to caller]
    C -- yes --> E[Call CSVPy.run()]
    E --> F{CSVPy.run() completes normally?}
    F -- yes --> G[Function returns None]
    F -- no --> H[Runtime exception or SystemExit propagates to caller]

## Examples:
- Typical packaging usage (conceptual):
  - Register this function as a console_scripts entry point so the packaging/runtime imports the module and calls launch_new_instance() to start the CSVPy utility. The packaging runner does the import and immediate call at process start.

- Programmatic invocation with error handling:
  - Call launch_new_instance() from a test harness or integration runner and catch expected failures:
      try:
          launch_new_instance()
      except NameError:
          # CSVPy class not available in this runtime/module
          handle_missing_entry_point()
      except SystemExit:
          # Argument parsing or explicit exit occurred in CSVPy.run(); handle if appropriate
          handle_exit_condition()
      except Exception as exc:
          # Other runtime errors from CSVPy.run() (I/O, agate parsing errors, etc.)
          handle_runtime_error(exc)

Notes:
- For details about what happens during CSVPy.run() (argument flags registered, rejection of sys.stdin input, which agate loader is chosen, interactive shell selection and its behavior), consult the CSVPy component documentation. This wrapper intentionally remains a minimal bootstrap and delegates all operational responsibilities to CSVPy.

