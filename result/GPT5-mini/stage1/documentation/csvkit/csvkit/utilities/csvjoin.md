# `csvjoin.py`

## `csvkit.utilities.csvjoin.CSVJoin` · *class*

*No documentation generated.*

### `csvkit.utilities.csvjoin.CSVJoin.add_arguments` · *method*

## Summary:
Adds the command-line arguments used by the CSV join utility to the instance's argument parser, mutating the parser state to accept inputs and options required for performing joins.

## Description:
This method registers the set of command-line options and positional arguments that control how the CSV join utility behaves. It is intended to be called during CLI setup when the utility's argument parser is being constructed — i.e., before parsing the actual command-line arguments and before the utility's main execution logic runs. Keeping argument registration in its own method isolates CLI definition from parsing and execution logic, making the code easier to read, test, and reuse across different CLI entrypoints or test harnesses.

Known callers and invocation context:
- Invoked during the CLI initialization/configuration phase for the CSV join utility. In typical CLI frameworks, a driver constructs the utility instance and calls its argument-registration method to prepare the ArgumentParser before calling parse_args() and executing the command. (The method body itself only mutates self.argparser and does not perform parsing or execution.)

Why this is a separate method:
- Encapsulates all CLI option definitions in one place for clarity and maintainability.
- Enables unit testing of argument definitions separately from parsing/execution.
- Follows the common pattern of separating parser construction from runtime logic.

## Args:
None (this is an instance method; it does not accept external parameters)

However, the method adds the following arguments to self.argparser (names, dests and defaults exactly as registered):

- Positional FILE argument:
    - metavar: 'FILE'
    - nargs: '*' (zero or more)
    - dest: 'input_paths'
    - default: ['-']
    - help: 'The CSV files to operate on. If only one is specified, it will be copied to STDOUT.'

- -c / --columns:
    - option strings: '-c', '--columns'
    - dest: 'columns'
    - type: string (as provided on command line)
    - help: Describes column name(s) or index(es) for joining; accepts either a single value or a comma-separated list with one identifier per file in the same order files are provided. If omitted, joining falls back to sequential (no matching) for multiple files.

- --outer:
    - option string: '--outer'
    - dest: 'outer_join'
    - action: store_true (boolean flag)
    - help: 'Perform a full outer join, rather than the default inner join.'

- --left:
    - option string: '--left'
    - dest: 'left_join'
    - action: store_true
    - help: Performs a left outer join; when more than two files are provided this is executed as a left-sequence of joins starting from the left.

- --right:
    - option string: '--right'
    - dest: 'right_join'
    - action: store_true
    - help: Performs a right outer join; when more than two files are provided this is executed as a right-sequence of joins starting from the right.

- -y / --snifflimit:
    - option strings: '-y', '--snifflimit'
    - dest: 'sniff_limit'
    - type: int
    - default: 1024
    - help: Limits CSV dialect sniffing to the given number of bytes; special values: "0" disables sniffing entirely, "-1" sniffs the entire file.

- -I / --no-inference:
    - option strings: '-I', '--no-inference'
    - dest: 'no_inference'
    - action: store_true
    - help: 'Disable type inference when parsing CSV input.'

## Returns:
None. The method returns nothing (implicitly returns None). Its effect is the mutation of self.argparser by registering new arguments; there is no other return value or object produced.

## Raises:
- AttributeError: If self.argparser does not exist or does not provide an add_argument method, an AttributeError (or similar exception from the underlying object) will be raised when attempting to call self.argparser.add_argument.
- TypeError or ValueError: If the underlying parser's add_argument validation rejects any provided parameter (e.g., invalid combination of kwargs), those lower-level exceptions from the parser may propagate. The method itself does not explicitly raise exceptions.

## State Changes:
Attributes READ:
- self.argparser — the method calls add_argument on this attribute.

Attributes WRITTEN / Mutated:
- self.argparser (mutated) — multiple arguments are registered on the parser object. No other self.<attr> fields on the instance are assigned or directly modified by this method.

## Constraints:
Preconditions:
- self.argparser must be initialized and must implement an add_argument method with semantics like argparse.ArgumentParser.add_argument.
- The environment should supply string/int CLI values that match the declared types when the parser later parses arguments (e.g., sniff_limit must parse as int).

Postconditions:
- After successful execution, self.argparser will accept:
    - A positional list of zero-or-more FILE paths via the 'input_paths' dest (defaulting to ['-']).
    - The named options and flags listed above with the specified dest names and defaults.
- No other attributes on self are modified by this call.

## Side Effects:
- Mutates the internal configuration of self.argparser (registers new options and positional arguments).
- Does not perform any I/O, network calls, file reads/writes, or global state changes beyond the parser mutation.

### `csvkit.utilities.csvjoin.CSVJoin.main` · *method*

*No documentation generated.*

### `csvkit.utilities.csvjoin.CSVJoin._parse_join_column_names` · *method*

## Summary:
Parse a comma-separated join column specification string into an ordered list of trimmed column name tokens and return it without modifying the object state.

## Description:
This helper extracts individual column identifiers from a single CLI-provided string (the value of the --columns / -c argument) by splitting on commas and trimming whitespace from each token.

Known callers and context:
- CSVJoin.main: called immediately after argument parsing when self.args.columns is provided. The returned list is used to validate the number of join columns and then to locate column indices in each input table prior to performing join operations.
Lifecycle stage: invoked during CLI input validation / preprocessing, before CSV files are read into agate.Table objects and before match_column_identifier is called.

Why a separate method:
- Keeps CLI argument parsing logic isolated and easily testable.
- Provides a single place to change splitting/normalization behavior (e.g., to support alternative separators) without touching main control flow.
- Improves readability by abstracting the small but self-contained transformation out of main.

## Args:
    join_string (str): The raw join-column specification string provided by the user (e.g., "id, user_id" or "0, 2").
        - Required format: a string containing column identifiers separated by commas.
        - Not None. The caller is expected to pass a truthy string (CSVJoin.main only calls this when args.columns is present).

## Returns:
    list[str]: An ordered list of column name tokens produced by splitting join_string on commas, with leading and trailing whitespace removed from each token.
    - The list length equals the number of comma-separated segments in join_string (e.g., "a,b" -> 2, "a,,b" -> 3).
    - Empty segments are preserved as empty strings after trimming (e.g., ",a" -> ["", "a"], "  " -> [""]).
    - For an input string with no commas, returns a single-element list with the trimmed string (e.g., " col " -> ["col"]).

## Raises:
    AttributeError: If join_string does not implement a split method (for example, if join_string is None or an int); the call join_string.split(',') will raise this.
    TypeError: If join_string.split(',') returns non-str elements (for example bytes on some inputs) such that str.strip cannot accept them; this will raise a TypeError when attempting to strip each element.
    (Note: callers in CSVJoin.main only invoke this method when args.columns is present and expected to be a string, so these exceptions indicate incorrect usage or a programming error.)

## State Changes:
Attributes READ:
    - None. The method does not read any self.<attr> fields.
Attributes WRITTEN:
    - None. The method does not modify self or any external objects.

## Constraints:
Preconditions:
    - join_string must be a str (or at least provide a split(',') that returns an iterable of str-like objects).
    - The method assumes callers already validated presence of args.columns where appropriate; it does not perform presence checks itself.

Postconditions:
    - Returns a list of strings in the same order as their appearance in join_string, each with leading/trailing whitespace removed.
    - Does not alter the CSVJoin instance state.

## Side Effects:
    - None. This method performs pure string manipulation and does not perform I/O, external service calls, or mutate objects outside of constructing and returning the resulting list.

## `csvkit.utilities.csvjoin.launch_new_instance` · *function*

## Summary:
Create a new CSVJoin CLI utility instance and invoke its run lifecycle, acting as a minimal importable entry point that boots the CSVJoin command.

## Description:
- Known callers within the codebase and typical context:
    - No direct internal callers found. The common callers are external packaging or runner code (for example, console_scripts entry_points registered in package metadata) and integration tests that need to start the csvjoin utility programmatically.
    - Typical trigger: the packaging runner imports this module and calls the function at process start to hand control to the CSVJoin implementation which performs argument parsing and CSV processing.

- Why this logic is extracted into its own function:
    - Provides a stable, importable, and testable entry point for external runners and packaging entry_points without exposing the CSVJoin class name or internals.
    - Keeps packaging configuration simple and uniform across csvkit utilities by adopting the one-function bootstrap convention used throughout the utilities package.
    - Separates instantiation/bootstrapping concerns from CSVJoin (which implements argument handling, I/O, and CSV processing).

## Args:
- None. This function accepts no parameters.

## Returns:
- None (implicitly). The function does not return a value; any observable effects are produced by CSVJoin.run().
- Possible outcomes:
    - Normal completion: CSVJoin.run completed and the function returned implicitly (None).
    - Abnormal termination: CSVJoin.run raised an exception or called sys.exit (SystemExit); the exception propagates and the function does not return normally.

## Raises:
- NameError
    - Condition: CSVJoin is not defined or importable in the module namespace at call time; attempting to call CSVJoin() raises NameError.
- Any exception raised by CSVJoin.__init__
    - Condition: constructor raises during instantiation (configuration or initialization error). The exception propagates unchanged.
- Any exception raised by CSVJoin.run (including SystemExit)
    - Condition: runtime errors during argument parsing, CSV I/O, column resolution, or explicit process termination. These exceptions propagate unchanged.

## Constraints:
- Preconditions:
    - The CSVJoin symbol must be defined and importable in the same module (or otherwise available in the module namespace) before calling this function.
    - Any runtime context expected by CSVJoin.run (for example, properly populated sys.argv, available stdin/stdout, or required environment variables) must be prepared by the caller; this function does not validate or set up runtime context.
- Postconditions:
    - If the function returns normally, CSVJoin.run executed to completion without raising an exception that escaped to the caller.
    - No return value is provided; side effects performed by CSVJoin.run (if any) have already occurred.

## Side Effects:
- The function itself performs no direct I/O. All side effects are produced by CSVJoin.run and may include:
    - Reading CSV input from files or stdin.
    - Writing CSV output to stdout or files.
    - Writing diagnostic messages to stderr.
    - Mutating process-level state (for example, calling sys.exit which raises SystemExit and can terminate the process).
    - Raising exceptions that propagate to the caller.

## Control Flow:
flowchart TD
    A[Call launch_new_instance()] --> B[Instantiate CSVJoin()]
    B --> C{CSVJoin.__init__ succeeds?}
    C -- no --> D[Constructor exception propagates (function does not handle it)]
    C -- yes --> E[Call CSVJoin.run()]
    E --> F{CSVJoin.run completes normally?}
    F -- no --> G[Runtime exception or SystemExit propagates]
    F -- yes --> H[Function returns None]

## Examples:
- Typical packaging usage (conceptual):
    - Register csvkit.utilities.csvjoin:launch_new_instance as a console_scripts entry point so the packaging runner imports and calls it to start the utility.

- Programmatic invocation with error handling:
    try:
        launch_new_instance()
    except NameError:
        # CSVJoin class not present in this module
        print("csvjoin entry point not available", file=sys.stderr)
        raise
    except SystemExit:
        # CSVJoin.run may call sys.exit; allow or handle as appropriate
        raise
    except Exception as exc:
        # Handle initialization or runtime errors raised by CSVJoin
        print("csvjoin failed:", exc, file=sys.stderr)
        raise

