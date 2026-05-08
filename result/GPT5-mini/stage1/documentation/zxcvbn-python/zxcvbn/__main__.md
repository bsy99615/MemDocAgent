# `__main__.py`

## `zxcvbn.__main__.JSONEncoder` · *class*

## Summary:
A json.JSONEncoder subclass that attempts the standard JSON encoding for an object and falls back to the object's string representation when the default encoder cannot serialize it.

## Description:
This class exists to make JSON serialization robust when encountering objects that the standard json.JSONEncoder.default cannot handle. Instead of raising a TypeError when an object is not directly serializable, this encoder converts the object to its string representation (str(object)) and returns that so the overall JSON serialization can proceed.

Typical scenarios:
- Serializing results from a password strength analysis or CLI tool where some returned values may be non-primitive types (custom objects, enums), and the program prefers readable string fallbacks over failing serialization.
- Used as the cls parameter to json.dumps or passed as an instantiated encoder to json.JSONEncoder.encode()/iterencode().

Known caller patterns:
- json.dumps(obj, cls=JSONEncoder)
- JSONEncoder().encode(obj)

Motivation and responsibility boundary:
- Responsibility: provide a single, well-defined fallback for non-serializable objects by returning their string form.
- Boundary: It does not attempt to serialize arbitrary complex types into structured JSON (e.g., converting objects to dicts). It only returns what the base JSONEncoder would produce, or str(o) when the base encoder raises TypeError.

## State:
- Attributes added by this subclass: none.
- Inherited state: all attributes and configuration options from json.JSONEncoder (e.g., ensure_ascii, separators, indent, sort_keys, etc.) remain available and behave as in the stdlib encoder. This subclass does not add or mutate stored state.
- __init__ parameters: not overridden. Instantiation accepts the same keyword arguments as json.JSONEncoder.__init__ (all optional). No additional constraints.

Class invariants:
- The class does not change or depend on any mutable global state.
- For any call default(o):
  - If the base class default(o) returns without raising TypeError, that return value is forwarded.
  - If the base class default(o) raises TypeError, this implementation returns str(o).
- Only TypeError raised by the base class default is caught and triggers the fallback; any other exception types raised by the base class or str(o) are propagated.

## Lifecycle:
Creation:
- Instantiate with no required arguments: encoder = JSONEncoder()
- Optional keyword arguments supported are those accepted by json.JSONEncoder (e.g., indent, ensure_ascii). These are forwarded to the base class __init__.

Usage:
- Typical use 1: pass as cls to json.dumps: json.dumps(value, cls=JSONEncoder)
- Typical use 2: create an instance and call encode or iterencode: JSONEncoder().encode(value)
- The only method this subclass provides is default(o); encoding flow is controlled by json.dumps / json.JSONEncoder, which will call default(o) for objects it cannot natively serialize.
- No special call ordering is required beyond the standard JSON encoding sequence.

Destruction:
- No special cleanup required. The class is not a context manager and does not hold external resources.

## Method Map:
Flowchart (Mermaid notation) showing the decision flow when default(o) is invoked:

graph LR
  A[json encoder needs to encode object o] --> B[Call JSONEncoder.default(o)]
  B --> C[Call super().default(o)]
  C -->|returns serializable value| D[Return that value to encoder]
  C -->|raises TypeError| E[Return str(o)]
  C -->|raises other exception| F[Propagate exception]

(Interpretation: the subclass delegates to the parent default; on a TypeError fallback to str(o); other exceptions bubble up.)

## Raises:
- __init__: raises whatever exceptions json.JSONEncoder.__init__ may raise for invalid arguments (e.g., TypeError if unexpected keyword arguments are supplied). This class does not add new __init__-time exceptions.
- default(o):
  - Will not raise TypeError for objects that were previously causing a TypeError in the base default because it catches TypeError and returns str(o).
  - If str(o) itself raises an exception (any exception type), that exception is not caught by this method and will propagate to the caller.
  - If the base class default raises exceptions other than TypeError, those exceptions are not caught here and will propagate unchanged.

## Example:
- Use as a safe encoder for json.dumps so unknown object types produce readable strings instead of failing serialization:
  - Pass this class as the cls parameter to json.dumps to enable the fallback behavior.
- Instantiate directly if you need an encoder object and call encode():
  - Create an instance with optional JSONEncoder keyword args (indent, ensure_ascii, etc.), then call encode(value).

### `zxcvbn.__main__.JSONEncoder.default` · *method*

## Summary:
Delegates JSON serialization of an object to the parent json.JSONEncoder; if the parent cannot handle the object (raises TypeError), returns the object's string representation instead.

## Description:
This method is invoked by the JSON encoding machinery when an object cannot be serialized using the encoder's normal encoding rules. Typical invocation contexts include using this class as the encoder via json.dumps(..., cls=JSONEncoder) or json.dump(..., cls=JSONEncoder), or when json.JSONEncoder.encode/iterencode reaches a value for which it calls the encoder's default method.

This logic is separated into its own method because it implements the fallback behavior for handling arbitrary objects: first try the base-class/default implementation (which may provide specialized encodings), and only if that fails with a TypeError provide a generic, safe fallback (the result of str(o)). Centralizing this two-step approach in a single method ensures consistent fallback semantics for all uses of this encoder.

## Args:
    o (Any): The object to be encoded. No further constraints; may be any Python object.

## Returns:
    Any:
        - If the superclass implementation (json.JSONEncoder.default) returns successfully, that exact value is returned unchanged.
        - If the superclass raises TypeError (indicating it cannot serialize the object), returns str(o) — a Python str representation of the object — which is JSON-serializable as a JSON string.
        - Note: the return type therefore is usually a JSON-serializable value; in the fallback case it is a str.

## Raises:
    Any exception raised by the superclass implementation other than TypeError will propagate unchanged.
    Any exception raised while converting the object to a string (i.e., an exception from o.__str__ or str(o)) will also propagate unchanged.
    The method explicitly catches only TypeError from the super call and does not suppress other exception types.

## State Changes:
    Attributes READ:
        - None of self's attributes are accessed by this method.
    Attributes WRITTEN:
        - None. This method does not modify self.

## Constraints:
    Preconditions:
        - self should be an instance of this JSONEncoder (a subclass of json.JSONEncoder).
        - The caller (json encoding machinery) expects a JSON-serializable return value; callers should be prepared that non-serializable returns from the superclass (if any) will be passed through, or that the fallback is a string.

    Postconditions:
        - If the superclass can handle the object, its returned value is returned unchanged.
        - If the superclass raises TypeError, the method returns str(o).
        - No attributes on self are modified.

## Side Effects:
    - No I/O is performed.
    - No external services are called.
    - The only observable effect (outside the returned value) is that an exception other than TypeError from the superclass or from str(o) will propagate to the caller.

## `zxcvbn.__main__.cli` · *function*

## Summary:
Read a password from standard input (non-blocking) or interactively via getpass, analyze it with the zxcvbn password-strength API using any CLI-provided user inputs, and write the analysis as pretty-printed JSON to standard output.

## Description:
This function implements the command-line entry behavior for password analysis:
- It obtains command-line arguments by calling parser.parse_args() and uses args.user_input (whatever the CLI parser populated) as the user-provided context passed into the analysis function.
- It first performs a non-blocking check of sys.stdin; if input is available it reads the entire stdin stream and treats that as the password (stripping a trailing newline if present). If no data is ready on stdin it falls back to prompting the user with getpass.getpass() so the password is entered interactively without echo.
- It calls the top-level zxcvbn(...) function with the obtained password and args.user_input supplied as the user_inputs parameter.
- It serializes the returned analysis dictionary to stdout as formatted JSON (indent=2), using the module's JSONEncoder subclass to provide a safe fallback for non-serializable objects, and appends a final newline.

Known callers within the codebase:
- Intended as the module's CLI entry point (invoked when running the package/module as a script, e.g., python -m zxcvbn). The function itself has no parameters and is designed to be invoked directly by the module's __main__ logic or by a wrapper that exposes the CLI.

Why this logic is a separate function:
- Encapsulates all CLI-specific I/O and argument handling in one place so the zxcvbn analysis function can remain a pure API. Separating the CLI glue simplifies testing and allows reuse of the analysis function in other contexts (web, GUI, test harnesses) without terminal I/O concerns.

## Args:
This function accepts no parameters (signature: cli()). It obtains runtime inputs from:
- parser.parse_args(): returns an args namespace; this function reads args.user_input from that namespace and forwards it to zxcvbn as the user_inputs argument. The exact form, multiplicity, and default of args.user_input are determined by the ArgumentParser configuration (parser) elsewhere in the module; this function only forwards the parsed value unchanged.

## Returns:
None — the function has no return value. Its observable output is side-effectful: it writes the JSON-serialized analysis to standard output and returns control to the caller.

## Raises:
The function does not explicitly raise custom exceptions, but the following exceptions may propagate directly from the called operations:
- Any exception raised by parser.parse_args() (for example SystemExit when argparse deems arguments invalid) will propagate.
- IndexError if stdin is readable but produces an empty string such that password[-1] is accessed (the code does not guard against an empty read).
- Exceptions from getpass.getpass (rare; e.g., EOFError if interactive input stream closes).
- Any exception raised by zxcvbn(...) invoked with the supplied password and args.user_input (these exceptions are defined by that function and its dependencies).
- json.dump may raise exceptions if encoding fails for reasons not covered by JSONEncoder (for example if JSONEncoder itself raises when converting an object to str).
- OSError or ValueError from select.select if sys.stdin is not a selectable file descriptor on the platform (platform-dependent behavior).

## Constraints:
Preconditions:
- A variable named parser must exist in the module and provide parse_args(), returning a namespace with a user_input attribute; this function assumes that call succeeds.
- sys.stdin must be a file-like object appropriate for select.select() on the running platform. If select.select cannot operate on sys.stdin, an exception may be raised.
- The zxcvbn function and JSONEncoder class must be available in the module namespace.

Postconditions:
- If execution completes normally, a single JSON object representing the zxcvbn analysis has been written to stdout with two-space indentation and followed by a newline.
- No value is returned; any non-exceptional completion implies the JSON was written (subject to buffering or I/O errors).

## Side Effects:
- I/O:
  - Potentially reads from sys.stdin in non-blocking fashion (select.select with 0.0 timeout) and may read the entire stdin stream if data is present.
  - If stdin had no data, prompts for a password using getpass.getpass() (interactive input, no-echo).
  - Writes formatted JSON to sys.stdout using json.dump(..., cls=JSONEncoder) and then writes a trailing newline via sys.stdout.write('\n').
- External calls:
  - Calls zxcvbn(password, user_inputs=args.user_input) and therefore triggers whatever processing and side effects (if any) occur in that function and its dependencies.
- Global state:
  - This function does not intentionally mutate global variables in its body, but zxcvbn(...) may mutate globals (see zxcvbn documentation). The CLI function forwards args.user_input and does not copy or sanitize it.

## Control Flow:
flowchart TD
    A[Start CLI] --> B[args = parser.parse_args()]
    B --> C{stdin has data? (select.select with 0.0 timeout)}
    C -- yes --> D[password = sys.stdin.read() (entire stream)]
    D --> D1{password ends with '\n' ?}
    D1 -- yes --> D2[strip trailing newline -> password = password[:-1]]
    D1 -- no --> E[use password as read]
    C -- no --> F[password = getpass.getpass() (interactive prompt)]
    E --> G[res = zxcvbn(password, user_inputs=args.user_input)]
    F --> G
    G --> H[json.dump(res, sys.stdout, indent=2, cls=JSONEncoder)]
    H --> I[sys.stdout.write('\n')]
    I --> J[Exit CLI]

Notes:
- The non-blocking stdin check means the function supports both piped input (echo "pw" | python -m zxcvbn) and interactive use.
- The function reads the entire stdin stream if available; it does not attempt to read a single line only unless the provider sends only a line.

## Examples:
1) Read password from a pipe (non-interactive):
    # Shell:
    echo "hunter2" | python -m zxcvbn
    # Behavior:
    # - The echo provides data on stdin; the CLI reads the full stream, strips a trailing newline, runs zxcvbn("hunter2", user_inputs=args.user_input), and prints the JSON result to stdout.

2) Interactive prompt (no data on stdin):
    # Shell:
    python -m zxcvbn
    # Behavior:
    # - No stdin data is present; CLI prompts with getpass.getpass() for a password (no echo). After input, it runs zxcvbn and prints the result JSON.

3) Example error handling pattern when invoking programmatically:
    try:
        cli()  # when invoked inside a Python process
    except SystemExit:
        # argparse may call sys.exit on parse errors; handle or log as appropriate
        handle_argparse_error()
    except Exception as e:
        # zxcvbn or I/O could raise; handle or report
        handle_runtime_error(e)

Implementation hints for reimplementing:
- Use select.select([sys.stdin], [], [], 0.0) to detect available piped input without blocking.
- When reading stdin, call sys.stdin.read() to get the entire piped content and remove a trailing newline if present.
- Use getpass.getpass() to prompt interactively when no piped input is available.
- Call zxcvbn(password, user_inputs=args.user_input) exactly as shown.
- Serialize the result to stdout with json.dump(..., indent=2, cls=JSONEncoder) and ensure a final newline is written.
- Be cautious: reading stdin.read() may return an empty string (EOF); the original code indexes password[-1] without guarding for empty string which will raise IndexError — preserve this behavior if exact compatibility is required, or defensively guard against empty reads when reimplementing.

